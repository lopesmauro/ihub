from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    DeliveryViewSet,
    EventIngestionView,
    EventTypeViewSet,
    EventViewSet,
    RuleViewSet,
)


router = DefaultRouter()
router.register("event-types", EventTypeViewSet)
router.register("rules", RuleViewSet)
router.register("events", EventViewSet)
router.register("deliveries", DeliveryViewSet)

urlpatterns = [
    path("events/ingest/", EventIngestionView.as_view(), name="event-ingest"),
    path("", include(router.urls)),
]
