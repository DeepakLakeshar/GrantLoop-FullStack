import logging
from .models import Donation
from . import services

logger = logging.getLogger(__name__)


def handle_stripe_webhook(payload: dict) -> bool:
    """
    Placeholder logic to route and process Stripe webhook events.
    In production, this is called after validating stripe.Webhook.construct_event.
    """
    event_type = payload.get("type")
    data_object = payload.get("data", {}).get("object", {})

    # In Stripe, the payment intent maps to the checkout order ID
    gateway_order_id = data_object.get("id")
    if not gateway_order_id:
        return False

    try:
        donation = Donation.objects.get(gateway_order_id=gateway_order_id)
    except Donation.DoesNotExist:
        logger.warning(f"Donation not found for Stripe gateway order: {gateway_order_id}")
        return False

    if event_type == "payment_intent.succeeded":
        charges = data_object.get("charges", {}).get("data", [])
        gateway_transaction_id = charges[0].get("id") if charges else f"ch_mock_{gateway_order_id}"

        try:
            services.mark_donation_success(
                donation=donation,
                gateway_transaction_id=gateway_transaction_id,
            )
            return True
        except ValueError as e:
            logger.error(f"Error marking Stripe donation success: {e}")
            return False

    elif event_type == "payment_intent.payment_failed":
        try:
            services.mark_donation_failed(donation=donation)
            return True
        except ValueError as e:
            logger.error(f"Error marking Stripe donation failure: {e}")
            return False

    return False


def handle_razorpay_webhook(payload: dict) -> bool:
    """
    Placeholder logic to route and process Razorpay webhook events.
    In production, this validates HMAC signatures before executing transitions.
    """
    event_type = payload.get("event")
    payment_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})

    gateway_order_id = payment_entity.get("order_id")
    if not gateway_order_id:
        return False

    try:
        donation = Donation.objects.get(gateway_order_id=gateway_order_id)
    except Donation.DoesNotExist:
        logger.warning(f"Donation not found for Razorpay gateway order: {gateway_order_id}")
        return False

    if event_type == "payment.captured":
        gateway_transaction_id = payment_entity.get("id")
        try:
            services.mark_donation_success(
                donation=donation,
                gateway_transaction_id=gateway_transaction_id,
            )
            return True
        except ValueError as e:
            logger.error(f"Error marking Razorpay donation success: {e}")
            return False

    elif event_type == "payment.failed":
        try:
            services.mark_donation_failed(donation=donation)
            return True
        except ValueError as e:
            logger.error(f"Error marking Razorpay donation failure: {e}")
            return False

    return False
