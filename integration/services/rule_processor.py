import requests

from integration.models import Delivery, Event, Rule


def process_event(event_id: int):
    event = Event.objects.get(id=event_id)
    has_failure = False

    try:
        rules = Rule.objects.filter(
            event_type=event.event_type,
            is_active=True,
        ).order_by("id")

        for rule in rules:
            delivery = create_delivery(event, rule)

            if delivery.rule.action_type == Rule.ActionType.HTTP_REQUEST:
                execute_http_delivery(delivery)
            else:
                delivery.status = Delivery.Status.FAILED
                delivery.error_message = (
                    f"Unsupported action type: {delivery.rule.action_type}"
                )
                delivery.save(update_fields=["status", "error_message"])

            if delivery.status == Delivery.Status.FAILED:
                has_failure = True

        event.status = Event.Status.FAILED if has_failure else Event.Status.PROCESSED
        event.error_message = "One or more deliveries failed." if has_failure else ""
        event.save(update_fields=["status", "error_message"])
    except Exception as exc:
        event.status = Event.Status.FAILED
        event.error_message = str(exc)
        event.save(update_fields=["status", "error_message"])

    return event


def create_delivery(event, rule):
    return Delivery.objects.create(
        event=event,
        rule=rule,
        status=Delivery.Status.PENDING,
    )


def execute_http_delivery(delivery):
    rule_config = delivery.rule.config
    method = None
    url = None
    body = None

    try:
        method = rule_config["method"]
        url = rule_config["url"]
        body = delivery.event.payload

        delivery.rendered_request = {
            "method": method,
            "url": url,
            "body": body,
        }
        delivery.save(update_fields=["rendered_request"])

        response = requests.request(method, url, json=body, timeout=10)

        if 200 <= response.status_code < 300:
            delivery.status = Delivery.Status.DELIVERED
            delivery.error_message = ""
        else:
            delivery.status = Delivery.Status.FAILED
            delivery.error_message = f"HTTP {response.status_code}"
    except Exception as exc:
        delivery.status = Delivery.Status.FAILED
        delivery.error_message = str(exc)
        if not delivery.rendered_request:
            delivery.rendered_request = {
                "method": method,
                "url": url,
                "body": body,
            }
            delivery.save(update_fields=["rendered_request"])

    delivery.save(update_fields=["status", "error_message"])
    return delivery
