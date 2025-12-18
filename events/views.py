from rest_framework import generics, pagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Event
from .serializers import EventSerializer


class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class EventListView(generics.ListAPIView):
    """Provides a paginated list of ingested events."""

    serializer_class = EventSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = Event.objects.order_by("-start_date", "title")
        city = self.request.query_params.get("city")
        if city:
            qs = qs.filter(city__iexact=city.strip())
        return qs


class HealthcheckView(APIView):
    """Simple view to ensure the API is reachable."""

    def get(self, request):
        return Response({"status": "ok"})
