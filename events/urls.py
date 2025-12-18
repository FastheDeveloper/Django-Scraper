from django.urls import path

from .views import EventListView, HealthcheckView

app_name = "events"

urlpatterns = [
    path("health", HealthcheckView.as_view(), name="health"),
    path("events", EventListView.as_view(), name="events-list"),
]
