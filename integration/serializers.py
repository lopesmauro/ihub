from rest_framework import serializers

from .models import Delivery, Event, EventType, Rule


class EventTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventType
        fields = ("id", "name", "description", "is_active")
        read_only_fields = ("id",)


class HttpRequestConfigSerializer(serializers.Serializer):
    ALLOWED_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}

    method = serializers.CharField()
    url = serializers.URLField()

    def validate_method(self, value):
        if value not in self.ALLOWED_METHODS:
            allowed = ", ".join(sorted(self.ALLOWED_METHODS))
            raise serializers.ValidationError(
                f"Unsupported HTTP method. Expected one of: {allowed}."
            )
        return value


class RuleSerializer(serializers.ModelSerializer):
    config = HttpRequestConfigSerializer()

    class Meta:
        model = Rule
        fields = (
            "id",
            "name",
            "event_type",
            "action_type",
            "config",
            "is_active",
        )
        read_only_fields = ("id",)

    def validate_action_type(self, value):
        if value != Rule.ActionType.HTTP_REQUEST:
            raise serializers.ValidationError(
                "Only http.request rules are supported."
            )
        return value

    def validate(self, attrs):
        unknown_fields = set(getattr(self, "initial_data", {})) - set(self.fields)
        if unknown_fields:
            raise serializers.ValidationError(
                {
                    "non_field_errors": (
                        "Unsupported fields: "
                        f"{', '.join(sorted(unknown_fields))}."
                    )
                }
            )
        return attrs


class IncomingEventSerializer(serializers.Serializer):
    event_type = serializers.CharField()
    source = serializers.CharField()
    payload = serializers.DictField()


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = (
            "id",
            "event_type",
            "source",
            "payload",
            "status",
            "error_message",
            "created_at",
        )
        read_only_fields = fields


class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = (
            "id",
            "event",
            "rule",
            "rendered_request",
            "status",
            "error_message",
            "created_at",
        )
        read_only_fields = fields
