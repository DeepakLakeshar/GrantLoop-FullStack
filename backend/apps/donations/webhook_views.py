from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from .webhooks import handle_stripe_webhook, handle_razorpay_webhook
from grantloop.openapi import razorpay_webhook_schema, stripe_webhook_schema


class StripeWebhookView(APIView):
    """
    Webhook endpoint to receive Stripe payment status events.
    """
    permission_classes = [AllowAny]

    @stripe_webhook_schema
    def post(self, request, *args, **kwargs):
        payload = request.data
        if not isinstance(payload, dict):
            return Response({"error": "Invalid payload format"}, status=status.HTTP_400_BAD_REQUEST)

        success = handle_stripe_webhook(payload)
        if success:
            return Response({"status": "event processed"}, status=status.HTTP_200_OK)
        return Response({"error": "Failed to process event"}, status=status.HTTP_400_BAD_REQUEST)


class RazorpayWebhookView(APIView):
    """
    Webhook endpoint to receive Razorpay payment status events.
    """
    permission_classes = [AllowAny]

    @razorpay_webhook_schema
    def post(self, request, *args, **kwargs):
        payload = request.data
        if not isinstance(payload, dict):
            return Response({"error": "Invalid payload format"}, status=status.HTTP_400_BAD_REQUEST)

        success = handle_razorpay_webhook(payload)
        if success:
            return Response({"status": "event processed"}, status=status.HTTP_200_OK)
        return Response({"error": "Failed to process event"}, status=status.HTTP_400_BAD_REQUEST)
