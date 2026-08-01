from django.db import transaction
from django.db.models import F

from apps.campaigns.models import Campaign, TransparencyLog
from .models import Donation
from .gateways import get_payment_gateway


def get_donation(*, donation_id) -> Donation:
    """
    Retrieves a single Donation by its UUID primary key,
    pre-fetching the donor user and targeted campaign.
    """
    return Donation.objects.select_related("donor", "campaign").get(id=donation_id)


def list_campaign_donations(*, campaign_id):
    """
    Retrieves a queryset of all donations belonging to a campaign,
    sorted by newest transaction first.
    """
    return Donation.objects.filter(campaign_id=campaign_id).select_related("donor").order_by("-created_at")


def list_user_donations(*, user_id):
    """
    Retrieves a queryset of all donations made by a specific user,
    sorted by newest transaction first.
    """
    return Donation.objects.filter(donor_id=user_id).select_related("campaign").order_by("-created_at")


def initiate_donation(
    *,
    campaign: Campaign,
    donor=None,
    original_amount,
    original_currency: str,
    is_anonymous: bool = False,
) -> Donation:
    """
    Business entrypoint to initialize a donation request.
    Validates campaign suitability, decides the payment gateway to use,
    calls the gateway adapter to create the checkout order session, and
    saves the pending donation record to the database.
    """
    if campaign.status != "live":
        raise ValueError("Donations can only be made to live campaigns.")

    if original_amount <= 0:
        raise ValueError("Original donation amount must be greater than zero.")

    # Determine payment gateway (could be fetched dynamically from campaign configuration)
    gateway_type = "stripe"
    gateway = get_payment_gateway(gateway_type)

    # Call gateway adapter to construct order session context
    settled_currency = campaign.campaign_currency
    order_data = gateway.create_order(
        original_amount=original_amount,
        original_currency=original_currency,
        settled_currency=settled_currency,
    )

    # Double check uniqueness constraint
    if Donation.objects.filter(gateway_order_id=order_data["gateway_order_id"]).exists():
        raise ValueError("A donation with this gateway order ID already exists.")

    return Donation.objects.create(
        campaign=campaign,
        donor=donor,
        original_amount=original_amount,
        original_currency=original_currency,
        settled_amount=order_data["settled_amount"],
        settled_currency=order_data["settled_currency"],
        is_anonymous=is_anonymous,
        gateway_type=order_data["gateway_type"],
        gateway_order_id=order_data["gateway_order_id"],
        status="pending",
    )


def create_donation(
    *,
    campaign: Campaign,
    donor=None,
    original_amount,
    original_currency: str,
    settled_amount,
    settled_currency: str,
    is_anonymous: bool = False,
    gateway_type: str,
    gateway_order_id: str,
) -> Donation:
    """
    Directly creates a pending donation record.
    Useful for testing or offline manual registrations where session data is pre-computed.
    """
    if campaign.status != "live":
        raise ValueError("Donations can only be made to live campaigns.")

    if original_amount <= 0:
        raise ValueError("Original donation amount must be greater than zero.")

    if settled_amount <= 0:
        raise ValueError("Settled donation amount must be greater than zero.")

    if not gateway_order_id:
        raise ValueError("Gateway order identifier is required.")

    if Donation.objects.filter(gateway_order_id=gateway_order_id).exists():
        raise ValueError("A donation with this gateway order ID already exists.")

    return Donation.objects.create(
        campaign=campaign,
        donor=donor,
        original_amount=original_amount,
        original_currency=original_currency,
        settled_amount=settled_amount,
        settled_currency=settled_currency,
        is_anonymous=is_anonymous,
        gateway_type=gateway_type,
        gateway_order_id=gateway_order_id,
        status="pending",
    )


def mark_donation_success(*, donation: Donation, gateway_transaction_id: str) -> Donation:
    """
    Updates a donation's state to success.
    Verifies the transaction via the corresponding payment gateway adapter,
    increments the campaign raised totals, and logs the public TransparencyLog.
    """
    if not gateway_transaction_id:
        raise ValueError("Gateway transaction identifier is required.")

    # Call gateway adapter to verify payment validity
    gateway = get_payment_gateway(donation.gateway_type)
    verification = gateway.verify_payment(
        gateway_order_id=donation.gateway_order_id,
        gateway_transaction_id=gateway_transaction_id,
    )

    if not verification.verified:
        raise ValueError("Payment verification failed at the gateway provider.")

    with transaction.atomic():
        # Lock the donation record to prevent duplicate webhook callbacks
        donation = Donation.objects.select_for_update().get(id=donation.id)

        if donation.status == "success":
            return donation

        if donation.status != "pending":
            raise ValueError(f"Cannot mark a {donation.status} donation as successful.")

        donation.status = "success"
        donation.gateway_transaction_id = verification.transaction_id
        donation.save(update_fields=["status", "gateway_transaction_id", "updated_at"])

        # Lock and update the target campaign's raised amount using an F expression
        campaign = Campaign.objects.select_for_update().get(id=donation.campaign_id)
        campaign.raised_amount = F("raised_amount") + donation.settled_amount
        campaign.save(update_fields=["raised_amount", "updated_at"])

        # Log the success event to the public campaign timeline
        donor_display = "Anonymous donor" if donation.is_anonymous else (donation.donor.full_name if donation.donor else "Guest donor")
        action_text = f"Donation of {donation.original_amount} {donation.original_currency} received from {donor_display}."
        TransparencyLog.objects.create(campaign=campaign, action=action_text)

    return donation


def mark_donation_failed(*, donation: Donation) -> Donation:
    """
    Transitions a pending donation's state to failed.
    """
    with transaction.atomic():
        donation = Donation.objects.select_for_update().get(id=donation.id)

        if donation.status == "failed":
            return donation

        if donation.status != "pending":
            raise ValueError(f"Cannot mark a {donation.status} donation as failed.")

        donation.status = "failed"
        donation.save(update_fields=["status", "updated_at"])

    return donation


def refund_donation(*, donation: Donation) -> Donation:
    """
    Reverses a successful donation.
    Decrements the campaign's raised total and appends a refund entry to the
    campaign's public TransparencyLog.
    """
    with transaction.atomic():
        donation = Donation.objects.select_for_update().get(id=donation.id)

        if donation.status == "refunded":
            return donation

        if donation.status != "success":
            raise ValueError("Only successful donations can be refunded.")

        # Trigger gateway refund logic
        gateway = get_payment_gateway(donation.gateway_type)
        gateway.refund_payment(
            gateway_transaction_id=donation.gateway_transaction_id,
            amount=donation.settled_amount,
        )

        donation.status = "refunded"
        donation.save(update_fields=["status", "updated_at"])

        # Lock and adjust the target campaign's raised amount using an F expression
        campaign = Campaign.objects.select_for_update().get(id=donation.campaign_id)
        campaign.raised_amount = F("raised_amount") - donation.settled_amount
        campaign.save(update_fields=["raised_amount", "updated_at"])

        # Log the refund event on the campaign timeline
        donor_display = "Anonymous donor" if donation.is_anonymous else (donation.donor.full_name if donation.donor else "Guest donor")
        action_text = f"Refund of {donation.original_amount} {donation.original_currency} processed for {donor_display}."
        TransparencyLog.objects.create(campaign=campaign, action=action_text)

    return donation
