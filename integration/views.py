from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Delivery, Event, EventType, Rule
from .serializers import (
    DeliverySerializer,
    EventSerializer,
    EventTypeSerializer,
    IncomingEventSerializer,
    RuleSerializer,
)


class EventTypeViewSet(viewsets.ModelViewSet):
    serializer_class = EventTypeSerializer
    queryset = EventType.objects.order_by("name", "id")


class RuleViewSet(viewsets.ModelViewSet):
    serializer_class = RuleSerializer
    queryset = (
        Rule.objects.select_related("event_type")
        .order_by("event_type__name", "name", "id")
    )


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EventSerializer
    queryset = Event.objects.select_related("event_type").order_by(
        "-created_at",
        "-id",
    )


class DeliveryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DeliverySerializer
    queryset = (
        Delivery.objects.select_related(
            "event",
            "event__event_type",
            "rule",
            "rule__event_type",
        )
        .order_by("-created_at", "-id")
    )


class EventIngestionView(APIView):
    def post(self, request):
        from .services.rule_processor import process_event

        serializer = IncomingEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        event_type_name = serializer.validated_data["event_type"]
        try:
            event_type = EventType.objects.get(name=event_type_name, is_active=True)
        except EventType.DoesNotExist as exc:
            raise ValidationError(
                {"event_type": "Unknown or inactive event type."}
            ) from exc

        event = Event.objects.create(
            event_type=event_type,
            source=serializer.validated_data["source"],
            payload=serializer.validated_data["payload"],
            status=Event.Status.RECEIVED,
        )

        process_event(event.id)
        event.refresh_from_db(fields=["status"])

        return Response(
            {"event_id": event.id, "status": event.status},
            status=status.HTTP_201_CREATED,
        )
