from rest_framework.response import Response
from rest_framework.views import APIView


class HealthcheckView(APIView):
    """Simple view to ensure the API is reachable."""

    def get(self, request):
        return Response({"status": "ok"})
