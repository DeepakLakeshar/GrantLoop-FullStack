from django.urls import path
from apps.health.views import ChangelogView, HealthCheckView, VersionView

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="api-health"),
    path("version/", VersionView.as_view(), name="api-version"),
    path("changelog/", ChangelogView.as_view(), name="api-changelog"),
]
