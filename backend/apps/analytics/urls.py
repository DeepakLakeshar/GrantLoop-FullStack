from django.urls import path
from . import views

urlpatterns = [
    path("admin/", views.AdminDashboardView.as_view(), name="analytics-admin-dashboard"),
    path("ngo/", views.NGODashboardView.as_view(), name="analytics-ngo-dashboard"),
    path("donor/", views.DonorDashboardView.as_view(), name="analytics-donor-dashboard"),
    path("charts/<str:chart_type>/", views.ChartAggregationView.as_view(), name="analytics-charts"),
    path("leaderboards/<str:leaderboard_type>/", views.LeaderboardView.as_view(), name="analytics-leaderboards"),
]
