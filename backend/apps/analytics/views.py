from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from grantloop.openapi import analytics_dashboard_schema

from . import services, serializers, permissions


class AdminDashboardView(APIView):
    """
    GET /api/v1/analytics/admin/
    Returns comprehensive platform analytics exclusively for administrative users.
    """
    permission_classes = [permissions.IsAdminForAnalytics]

    @analytics_dashboard_schema
    def get(self, request):
        data = services.get_admin_dashboard(params=request.query_params.dict())
        serializer = serializers.AdminDashboardSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NGODashboardView(APIView):
    """
    GET /api/v1/analytics/ngo/
    Returns role-scoped analytical metrics and campaign progress exclusively for NGO users.
    """
    permission_classes = [permissions.IsNGOForAnalytics]

    @analytics_dashboard_schema
    def get(self, request):
        data = services.get_ngo_dashboard(user=request.user, params=request.query_params.dict())
        serializer = serializers.NGODashboardSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DonorDashboardView(APIView):
    """
    GET /api/v1/analytics/donor/
    Returns contributor lifetime metrics and activity feeds exclusively for donor users.
    """
    permission_classes = [permissions.IsDonorForAnalytics]

    @analytics_dashboard_schema
    def get(self, request):
        data = services.get_donor_dashboard(user=request.user, params=request.query_params.dict())
        serializer = serializers.DonorDashboardSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChartAggregationView(APIView):
    """
    GET /api/v1/analytics/charts/<chart_type>/
    Returns 12-month React-ready aggregated chart arrays for donations, payouts, campaigns, and users.
    """
    permission_classes = [permissions.IsAuthenticatedForAnalytics]
    serializer_class = serializers.ChartSerializer

    @extend_schema(tags=["Analytics"], summary="Retrieve Time-Series Monthly Chart Aggregation Arrays")
    def get(self, request, chart_type=None):
        valid_charts = {"donations", "payouts", "campaigns", "users"}
        if not chart_type or chart_type.lower().strip("/") not in valid_charts:
            return Response(
                {"error": f"Invalid chart type. Must be one of: {', '.join(sorted(valid_charts))}."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = services.get_monthly_chart(
            chart_type=chart_type,
            user=request.user,
            params=request.query_params.dict(),
        )
        serializer = serializers.ChartSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LeaderboardView(APIView):
    """
    GET /api/v1/analytics/leaderboards/<leaderboard_type>/
    Returns comparative entity leaderboards (top campaigns, NGOs, donors, activity, largest donations/payouts).
    """
    permission_classes = [permissions.IsAuthenticatedForAnalytics]
    serializer_class = serializers.LeaderboardSerializer

    @extend_schema(tags=["Analytics"], summary="Retrieve Comparative Performance Entity Leaderboards")
    def get(self, request, leaderboard_type=None):
        valid_leaderboards = {
            "top-campaigns", "top-ngos", "top-donors",
            "highest-raised-campaigns", "most-active-campaigns",
            "largest-donations", "largest-payouts",
            "top_campaigns", "top_ngos", "top_donors",
            "highest_raised_campaigns", "most_active_campaigns",
            "largest_donations", "largest_payouts",
        }
        if not leaderboard_type or leaderboard_type.lower().strip("/") not in valid_leaderboards:
            return Response(
                {"error": "Invalid leaderboard type specified."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = services.get_leaderboard(
            leaderboard_type=leaderboard_type,
            params=request.query_params.dict(),
        )
        serializer = serializers.LeaderboardSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
