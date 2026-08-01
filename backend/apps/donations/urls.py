from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import DonationViewSet
from .webhook_views import StripeWebhookView, RazorpayWebhookView

router = DefaultRouter()
router.register("donations", DonationViewSet, basename="donation")

urlpatterns = [
    path("donations/webhooks/stripe/", StripeWebhookView.as_view(), name="stripe-webhook"),
    path("donations/webhooks/razorpay/", RazorpayWebhookView.as_view(), name="razorpay-webhook"),
] + router.urls
