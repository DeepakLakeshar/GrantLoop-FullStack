from rest_framework.routers import DefaultRouter

from .views import (
    CampaignViewSet,
    CategoryViewSet,
    TransparencyLogViewSet,
    VerificationViewSet,
)

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("campaigns", CampaignViewSet, basename="campaign")
router.register("verifications", VerificationViewSet, basename="verification")
router.register("transparency-logs", TransparencyLogViewSet, basename="transparency-log")

urlpatterns = router.urls
