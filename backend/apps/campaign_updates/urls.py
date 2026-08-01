from rest_framework.routers import DefaultRouter

from .views import CampaignUpdateViewSet

router = DefaultRouter()
router.register("campaign-updates", CampaignUpdateViewSet, basename="campaignupdate")

urlpatterns = router.urls
