from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("django_prometheus.urls")),
    # --- Public System Uptime, Versioning, and Release Changelog Feeds ---
    path("api/", include("apps.health.urls")),
    path("api/performance/", include("apps.performance.urls")),
    path("api/v1/performance/", include("apps.performance.urls")),
    # --- OpenAPI 3.0 Documentation & Interactive Portal Endpoints ---
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # --- GrantLoop Core Domain API v1 Routes ---
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/analytics/", include("apps.analytics.urls")),
    path("api/v1/reports/", include("apps.reports.urls")),
    path("api/v1/ngo-profile/", include("apps.ngo_profiles.urls")),
    path("api/v1/", include("apps.beneficiaries.urls")),
    path("api/v1/", include("apps.campaigns.urls")),
    path("api/v1/", include("apps.milestones.urls")),
    path("api/v1/", include("apps.campaign_updates.urls")),
    path("api/v1/", include("apps.documents.urls")),
    path("api/v1/", include("apps.execution_partners.urls")),
    path("api/v1/", include("apps.donations.urls")),
    path("api/v1/", include("apps.notifications.urls")),
    path("api/v1/", include("apps.payouts.urls")),
]
