from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/", include("apps.beneficiaries.urls")),
    path("api/v1/", include("apps.campaigns.urls")),
    path("api/v1/", include("apps.milestones.urls")),
    path("api/v1/", include("apps.campaign_updates.urls")),
    path("api/v1/", include("apps.documents.urls")),
    path("api/v1/", include("apps.execution_partners.urls")),
    path("api/v1/", include("apps.donations.urls")),
    path("api/v1/", include("apps.notifications.urls")),
    path("api/v1/", include("apps.payouts.urls")),
    path("api/v1/ngo-profile/", include("apps.ngo_profiles.urls")),
]
