from django.urls import path
from .views import PerformanceMetricsView

urlpatterns = [
    path("", PerformanceMetricsView.as_view(), name="performance-metrics"),
]
