import logging
from django.contrib.auth import get_user_model
from apps.notifications.services import create_notification, create_notifications
from apps.notifications.models import NotificationType

logger = logging.getLogger(__name__)
User = get_user_model()


def notify_payout_requested(payout) -> None:
    """
    Dispatches notifications when an NGO requests a fund withdrawal.
    Notifies the NGO owner confirming submission and alerts administrative approvers.
    """
    try:
        # Confirm to NGO
        create_notification(
            recipient=payout.ngo,
            title="Payout Request Submitted",
            message=f"Your payout request of {payout.requested_amount} {payout.currency} for campaign '{payout.campaign.title}' has been submitted for review.",
            notification_type=NotificationType.PAYOUT_REQUESTED,
            action_url=f"/payouts/{payout.id}/",
        )

        # Notify active admin supervisors
        admin_users = list(User.objects.filter(role="admin", is_active=True))
        if admin_users:
            create_notifications(
                recipients=admin_users,
                title="New Payout Request Pending Review",
                message=f"NGO '{payout.ngo.email}' requested {payout.requested_amount} {payout.currency} for campaign '{payout.campaign.title}'.",
                notification_type=NotificationType.PAYOUT_REQUESTED,
                action_url=f"/payouts/{payout.id}/",
            )
    except Exception as exc:
        logger.error(f"Failed to dispatch payout request notifications: {exc}")


def notify_payout_approved(payout) -> None:
    """
    Dispatches notification to NGO upon administrative payout authorization.
    """
    try:
        approved_amt = payout.approved_amount if payout.approved_amount is not None else payout.requested_amount
        create_notification(
            recipient=payout.ngo,
            title="Payout Request Approved",
            message=f"Your payout request for campaign '{payout.campaign.title}' has been approved for {approved_amt} {payout.currency}.",
            notification_type=NotificationType.PAYOUT_APPROVED,
            action_url=f"/payouts/{payout.id}/",
        )
    except Exception as exc:
        logger.error(f"Failed to dispatch payout approval notification: {exc}")


def notify_payout_rejected(payout, rejection_reason: str = "") -> None:
    """
    Dispatches notification to NGO upon administrative payout rejection.
    """
    try:
        msg = f"Your payout request for campaign '{payout.campaign.title}' was rejected."
        if rejection_reason or payout.failure_reason:
            msg += f" Reason: {rejection_reason or payout.failure_reason}"
        create_notification(
            recipient=payout.ngo,
            title="Payout Request Rejected",
            message=msg,
            notification_type=NotificationType.PAYOUT_REJECTED,
            action_url=f"/payouts/{payout.id}/",
        )
    except Exception as exc:
        logger.error(f"Failed to dispatch payout rejection notification: {exc}")


def notify_payout_processing(payout) -> None:
    """
    Dispatches notification when a fund disbursement order enters gateway processing status.
    """
    try:
        create_notification(
            recipient=payout.ngo,
            title="Payout Processing Started",
            message=f"Your payout transfer of {payout.approved_amount or payout.requested_amount} {payout.currency} for campaign '{payout.campaign.title}' is currently processing.",
            notification_type=NotificationType.PAYOUT_PROCESSING,
            action_url=f"/payouts/{payout.id}/",
        )
    except Exception as exc:
        logger.error(f"Failed to dispatch payout processing notification: {exc}")


def notify_payout_completed(payout) -> None:
    """
    Dispatches notification to NGO confirming successful fund disbursement settlement.
    """
    try:
        create_notification(
            recipient=payout.ngo,
            title="Payout Transfer Completed",
            message=f"Your fund withdrawal of {payout.approved_amount or payout.requested_amount} {payout.currency} for campaign '{payout.campaign.title}' has been successfully completed.",
            notification_type=NotificationType.PAYOUT_COMPLETED,
            action_url=f"/payouts/{payout.id}/",
        )
    except Exception as exc:
        logger.error(f"Failed to dispatch payout completion notification: {exc}")


def notify_payout_failed(payout, failure_reason: str = "") -> None:
    """
    Dispatches alert notification when an in-progress transfer collapses at the provider gateway.
    """
    try:
        msg = f"Your payout transfer for campaign '{payout.campaign.title}' failed during execution."
        if failure_reason or payout.failure_reason:
            msg += f" Reason: {failure_reason or payout.failure_reason}"
        create_notification(
            recipient=payout.ngo,
            title="Payout Transfer Failed",
            message=msg,
            notification_type=NotificationType.PAYOUT_FAILED,
            action_url=f"/payouts/{payout.id}/",
        )
    except Exception as exc:
        logger.error(f"Failed to dispatch payout failure notification: {exc}")


def notify_payout_cancelled(payout) -> None:
    """
    Dispatches notification confirming a pending payout request cancellation.
    """
    try:
        create_notification(
            recipient=payout.ngo,
            title="Payout Request Cancelled",
            message=f"Your payout request of {payout.requested_amount} {payout.currency} for campaign '{payout.campaign.title}' has been cancelled.",
            notification_type=NotificationType.PAYOUT_CANCELLED,
            action_url=f"/payouts/{payout.id}/",
        )
    except Exception as exc:
        logger.error(f"Failed to dispatch payout cancellation notification: {exc}")
