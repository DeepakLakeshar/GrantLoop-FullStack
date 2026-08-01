import uuid
from decimal import Decimal
from django.core.exceptions import PermissionDenied
from django.db import transaction, models
from django.utils import timezone

from apps.campaigns.models import Campaign, TransparencyLog
from .models import Payout, PayoutStatus
from .gateways import get_payout_gateway
from . import events


def get_available_balance(campaign: Campaign, excluding_payout_id=None) -> Decimal:
    """
    Calculates withdrawable fund balance for a campaign.
    Formula: Total funds raised minus amounts reserved or disbursed in active payouts
    (pending, approved, processing, completed).
    Excludes rejected, failed, cancelled, and soft-deleted payouts.
    All monetary calculations explicitly enforce Decimal arithmetic.
    """
    total_raised = Decimal(str(campaign.raised_amount or "0.00"))

    active_payouts = Payout.objects.filter(
        campaign=campaign,
        is_deleted=False,
        status__in=[
            PayoutStatus.PENDING,
            PayoutStatus.APPROVED,
            PayoutStatus.PROCESSING,
            PayoutStatus.COMPLETED,
        ],
    )
    if excluding_payout_id:
        active_payouts = active_payouts.exclude(id=excluding_payout_id)

    reserved_total = Decimal("0.00")
    for p in active_payouts:
        amt = p.approved_amount if p.approved_amount is not None else p.requested_amount
        reserved_total += Decimal(str(amt))

    available = total_raised - reserved_total
    return max(Decimal("0.00"), available)


def list_payouts(*, user):
    """
    Retrieves a queryset of payouts scoped by user role.
    Admins view all active platform payouts. NGOs view payouts for their own campaigns.
    Donors are entirely blocked.
    """
    if not user or not user.is_authenticated:
        return Payout.objects.none()
    if getattr(user, "role", None) == "admin":
        return Payout.objects.select_related("ngo", "campaign", "requested_by", "approved_by").all()
    elif getattr(user, "role", None) == "ngo":
        return Payout.objects.filter(campaign__created_by=user).select_related("ngo", "campaign", "requested_by", "approved_by")
    return Payout.objects.none()


def get_payout(*, payout_id, user=None) -> Payout:
    """
    Retrieves a single payout by primary key.
    Admins can lookup soft-deleted or archived entries.
    """
    if user and getattr(user, "role", None) == "admin":
        queryset = Payout.objects.all_with_deleted()
    else:
        queryset = Payout.objects.all()
    return queryset.select_related("ngo", "campaign", "requested_by", "approved_by").get(id=payout_id)


def create_payout_request(
    *,
    campaign: Campaign,
    user,
    requested_amount,
    currency: str = "INR",
    request_notes: str = "",
) -> Payout:
    """
    Entrypoint for NGOs to request campaign fund withdrawal.
    Enforces exhaustive invariants before transaction commitment:
    - User ownership / admin authorization
    - Campaign active state (live or completed)
    - Campaign verification status (must have approved verification record)
    - Milestone requirement completion
    - Positive amount validation
    - Available balance reservation locking against concurrency
    - Prevention of concurrent duplicate pending requests
    """
    if getattr(user, "role", None) != "admin" and campaign.created_by_id != user.id:
        raise PermissionDenied("Only the campaign owning NGO or an administrator can request a payout.")

    req_amt = Decimal(str(requested_amount))
    if req_amt <= Decimal("0.00"):
        raise ValueError("Requested payout amount must be greater than zero.")

    if campaign.status not in ["live", "completed"]:
        raise ValueError("Cannot request a payout for an inactive campaign.")

    # Check if campaign is verified
    if not campaign.verifications.filter(status="approved").exists():
        raise ValueError("Campaign has not been verified for fund withdrawals.")

    # Check if required milestones are complete
    if campaign.milestones.exists() and not campaign.milestones.filter(status="completed").exists():
        raise ValueError("Cannot request payout: required campaign milestones are not complete.")

    with transaction.atomic():
        # Lock campaign row to prevent race conditions during concurrent payout reservations
        locked_campaign = Campaign.objects.select_for_update().get(id=campaign.id)

        # Check existing pending payout requests
        if Payout.objects.filter(campaign=locked_campaign, status=PayoutStatus.PENDING, is_deleted=False).exists():
            raise ValueError("A pending payout request already exists for this campaign.")

        bal_before = get_available_balance(locked_campaign)
        if req_amt > bal_before:
            raise ValueError(f"Requested amount ({req_amt}) exceeds available campaign balance ({bal_before}).")

        bal_after = bal_before - req_amt

        payout = Payout.objects.create(
            ngo=locked_campaign.created_by,
            campaign=locked_campaign,
            requested_amount=req_amt,
            approved_amount=None,
            available_balance_before=bal_before,
            available_balance_after=bal_after,
            currency=currency,
            status=PayoutStatus.PENDING,
            request_notes=request_notes,
            requested_by=user,
        )

        events.notify_payout_requested(payout)

    return payout


def approve_payout(
    *,
    payout_id,
    admin_user,
    approved_amount=None,
    admin_notes: str = "",
) -> Payout:
    """
    Administrative approval of a pending payout request.
    Idempotent: returns existing instance if already approved.
    Locks records to safeguard against concurrent cancellation or conflicting approvals.
    """
    if getattr(admin_user, "role", None) != "admin":
        raise PermissionDenied("Only administrators can approve payout requests.")

    with transaction.atomic():
        payout = Payout.objects.all_with_deleted().select_for_update().get(id=payout_id)
        if payout.status == PayoutStatus.APPROVED:
            return payout

        if payout.status != PayoutStatus.PENDING:
            raise ValueError(f"Cannot approve payout in status '{payout.status}'.")

        # Lock associated campaign for safe balance re-evaluation
        locked_campaign = Campaign.objects.select_for_update().get(id=payout.campaign_id)
        app_amt = Decimal(str(approved_amount)) if approved_amount is not None else Decimal(str(payout.requested_amount))

        if app_amt <= Decimal("0.00"):
            raise ValueError("Approved amount must be greater than zero.")

        bal_before = get_available_balance(locked_campaign, excluding_payout_id=payout.id)
        if app_amt > bal_before:
            raise ValueError(f"Approved amount ({app_amt}) exceeds available balance ({bal_before}).")

        bal_after = bal_before - app_amt

        payout.status = PayoutStatus.APPROVED
        payout.approved_amount = app_amt
        payout.available_balance_before = bal_before
        payout.available_balance_after = bal_after
        payout.approved_by = admin_user
        payout.approved_at = timezone.now()
        if admin_notes:
            payout.admin_notes = admin_notes
        payout.save(
            update_fields=[
                "status",
                "approved_amount",
                "available_balance_before",
                "available_balance_after",
                "approved_by",
                "approved_at",
                "admin_notes",
                "updated_at",
            ]
        )

        events.notify_payout_approved(payout)

    return payout


def reject_payout(
    *,
    payout_id,
    admin_user,
    rejection_reason: str = "",
    admin_notes: str = "",
) -> Payout:
    """
    Administrative rejection of a pending payout request.
    Idempotent: returns instance if already rejected.
    Releases reserved balance automatically by transitioning out of active states.
    """
    if getattr(admin_user, "role", None) != "admin":
        raise PermissionDenied("Only administrators can reject payout requests.")

    with transaction.atomic():
        payout = Payout.objects.all_with_deleted().select_for_update().get(id=payout_id)
        if payout.status == PayoutStatus.REJECTED:
            return payout

        if payout.status != PayoutStatus.PENDING:
            raise ValueError(f"Cannot reject payout in status '{payout.status}'.")

        payout.status = PayoutStatus.REJECTED
        payout.approved_by = admin_user
        if rejection_reason:
            payout.failure_reason = rejection_reason
        if admin_notes:
            payout.admin_notes = admin_notes
        payout.save(update_fields=["status", "approved_by", "failure_reason", "admin_notes", "updated_at"])

        events.notify_payout_rejected(payout, rejection_reason=rejection_reason)

    return payout


def mark_processing(
    *,
    payout_id,
    admin_user,
    gateway_type: str = "mock",
    account_reference: str = "default_acct",
) -> Payout:
    """
    Initiates payment provider gateway disbursement.
    Idempotent: if repeated process requests occur, returns without triggering duplicate bank transfers.
    """
    if getattr(admin_user, "role", None) != "admin":
        raise PermissionDenied("Only administrators can initiate gateway processing.")

    with transaction.atomic():
        payout = Payout.objects.all_with_deleted().select_for_update().get(id=payout_id)
        if payout.status in [PayoutStatus.PROCESSING, PayoutStatus.COMPLETED]:
            return payout

        if payout.status != PayoutStatus.APPROVED:
            raise ValueError(f"Cannot process payout in status '{payout.status}'; must be approved first.")

        gateway = get_payout_gateway(gateway_type)
        transfer_amt = Decimal(str(payout.approved_amount if payout.approved_amount is not None else payout.requested_amount))

        result = gateway.initiate_transfer(
            account_reference=account_reference,
            amount=transfer_amt,
            currency=payout.currency,
            idempotency_key=f"pay_{payout.id.hex}",
        )

        payout.status = PayoutStatus.PROCESSING
        payout.gateway_reference = result.gateway_reference
        if result.transfer_reference:
            payout.transfer_reference = result.transfer_reference
        payout.save(update_fields=["status", "gateway_reference", "transfer_reference", "updated_at"])

        events.notify_payout_processing(payout)

    return payout


def mark_completed(
    *,
    payout_id,
    admin_user,
    transfer_reference: str = None,
) -> Payout:
    """
    Confirms successful settlement of funds to NGO.
    Idempotent: safe against repeated completion callbacks and duplicate webhooks.
    Logs an immutable audit event to the campaign's public TransparencyLog.
    """
    if getattr(admin_user, "role", None) != "admin":
        raise PermissionDenied("Only administrators can confirm payout completion.")

    with transaction.atomic():
        payout = Payout.objects.all_with_deleted().select_for_update().get(id=payout_id)
        if payout.status == PayoutStatus.COMPLETED:
            return payout

        if payout.status not in [PayoutStatus.APPROVED, PayoutStatus.PROCESSING]:
            raise ValueError(f"Cannot complete payout in status '{payout.status}'.")

        final_transfer_ref = transfer_reference
        if not final_transfer_ref:
            if payout.transfer_reference:
                final_transfer_ref = payout.transfer_reference
            elif payout.gateway_reference:
                # Attempt verification with provider
                gateway = get_payout_gateway("mock") # Default fallback for verification
                res = gateway.verify_transfer(gateway_reference=payout.gateway_reference)
                final_transfer_ref = res.transfer_reference
            else:
                final_transfer_ref = f"utr_{uuid.uuid4().hex[:12]}"

        payout.status = PayoutStatus.COMPLETED
        payout.transfer_reference = final_transfer_ref
        payout.save(update_fields=["status", "transfer_reference", "updated_at"])

        # Record immutable timeline entry
        amt = payout.approved_amount if payout.approved_amount is not None else payout.requested_amount
        action_text = f"Fund disbursement of {amt} {payout.currency} completed for campaign."
        TransparencyLog.objects.create(campaign=payout.campaign, action=action_text)

        events.notify_payout_completed(payout)

    return payout


def mark_failed(
    *,
    payout_id,
    admin_user,
    failure_reason: str = "Transfer failed during execution at payment gateway.",
) -> Payout:
    """
    Records failure of a disbursement transfer.
    Idempotent against duplicated failure callbacks. Releases reserved funds back to campaign balance.
    """
    if getattr(admin_user, "role", None) != "admin":
        raise PermissionDenied("Only administrators can mark payouts as failed.")

    with transaction.atomic():
        payout = Payout.objects.all_with_deleted().select_for_update().get(id=payout_id)
        if payout.status == PayoutStatus.FAILED:
            return payout

        if payout.status not in [PayoutStatus.APPROVED, PayoutStatus.PROCESSING]:
            raise ValueError(f"Cannot mark payout as failed from status '{payout.status}'.")

        payout.status = PayoutStatus.FAILED
        if failure_reason:
            payout.failure_reason = failure_reason
        payout.save(update_fields=["status", "failure_reason", "updated_at"])

        events.notify_payout_failed(payout, failure_reason=failure_reason)

    return payout


def cancel_payout(
    *,
    payout_id,
    user,
) -> Payout:
    """
    Cancels a payout request.
    Strictly enforced: cancellation is ONLY permitted while status == 'pending'.
    Can be initiated by the requesting NGO owner or platform administrators.
    Sets is_deleted=True to align with soft-delete patterns and DELETE API endpoint mapping.
    """
    with transaction.atomic():
        payout = Payout.objects.all_with_deleted().select_for_update().get(id=payout_id)

        # Authorize actor
        if getattr(user, "role", None) != "admin" and payout.ngo_id != user.id and payout.campaign.created_by_id != user.id:
            raise PermissionDenied("You do not have permission to cancel this payout request.")

        if payout.status == PayoutStatus.CANCELLED and payout.is_deleted:
            return payout

        if payout.status != PayoutStatus.PENDING:
            raise ValueError(f"Cannot cancel payout in status '{payout.status}': cancellation is only permitted while pending.")

        payout.status = PayoutStatus.CANCELLED
        payout.is_deleted = True
        payout.save(update_fields=["status", "is_deleted", "updated_at"])

        events.notify_payout_cancelled(payout)

    return payout
