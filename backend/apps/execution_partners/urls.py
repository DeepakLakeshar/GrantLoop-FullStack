from rest_framework.routers import DefaultRouter

from .views import ExecutionPartnerViewSet

router = DefaultRouter()
router.register("execution-partners", ExecutionPartnerViewSet, basename="execution-partner")

urlpatterns = router.urls
