from rest_framework import routers
from .views import PayoutViewSet

router = routers.DefaultRouter()
router.register(r"payouts", PayoutViewSet, basename="payout")

urlpatterns = router.urls
