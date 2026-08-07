from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse
from common.permissions import IsAdmin
from .services import PerformanceTracker


class PerformanceMetricsView(APIView):
    """
    GET /api/performance/
    Returns real-time enterprise caching, Redis, and slow query diagnostics.
    Restricted exclusively to platform administrators.
    """
    permission_classes = [IsAdmin]

    @extend_schema(
        tags=["Performance"],
        summary="Retrieve Platform Performance, Caching & Redis Diagnostics",
        description="Returns cache hit ratio, miss counts, Redis reachability, slow endpoint profiles, query counts, and server uptime.",
        responses={
            200: OpenApiResponse(description="Real-time performance telemetry JSON dictionary."),
            401: OpenApiResponse(description="Authentication required."),
            403: OpenApiResponse(description="Permission denied. Exclusive admin access required."),
        }
    )
    def get(self, request):
        metrics = PerformanceTracker.get_summary_metrics()
        return Response(metrics, status=status.HTTP_200_OK)
