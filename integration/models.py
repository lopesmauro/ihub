from django.db import models


class EventType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Rule(models.Model):
    class ActionType(models.TextChoices):
        HTTP_REQUEST = "http.request", "HTTP Request"

    name = models.CharField(max_length=100)
    event_type = models.ForeignKey(
        EventType,
        on_delete=models.CASCADE,
        related_name="rules",
    )
    action_type = models.CharField(
        max_length=30,
        choices=ActionType.choices,
        default=ActionType.HTTP_REQUEST,
    )
    config = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    class Status(models.TextChoices):
        RECEIVED = "RECEIVED", "Received"
        PROCESSED = "PROCESSED", "Processed"
        FAILED = "FAILED", "Failed"

    event_type = models.ForeignKey(
        EventType,
        on_delete=models.PROTECT,
        related_name="events",
    )
    source = models.CharField(max_length=100)
    payload = models.JSONField(default=dict)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.RECEIVED,
    )
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_type.name} from {self.source}"


class Delivery(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        DELIVERED = "DELIVERED", "Delivered"
        FAILED = "FAILED", "Failed"

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="deliveries",
    )
    rule = models.ForeignKey(
        Rule,
        on_delete=models.PROTECT,
        related_name="deliveries",
    )
    rendered_request = models.JSONField(default=dict)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_id}: {self.status}"
