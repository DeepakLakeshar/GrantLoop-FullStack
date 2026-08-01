from rest_framework.routers import DefaultRouter

from .views import BeneficiaryViewSet

router = DefaultRouter()
router.register("beneficiaries", BeneficiaryViewSet, basename="beneficiary")

urlpatterns = router.urls
