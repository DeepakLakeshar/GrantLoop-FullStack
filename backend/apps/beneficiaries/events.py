import logging
from apps.notifications.services import create_notification
from apps.notifications.models import NotificationType

logger = logging.getLogger(__name__)


def notify_beneficiary_verified(beneficiary) -> None:
    """
    Decoupled helper invoked when a beneficiary's verification succeeds.
    Sends notification to the campaign owner.
    """
    try:
        recipient = beneficiary.campaign.created_by
        create_notification(
            recipient=recipient,
            title="Beneficiary Verification Approved",
            message=f"Beneficiary '{beneficiary.full_name}' for campaign '{beneficiary.campaign.title}' has been verified.",
            notification_type=NotificationType.BENEFICIARY_VERIFIED,
            action_url=f"/beneficiaries/{beneficiary.id}/",
        )
    except Exception as e:
        logger.error(f"Failed to dispatch beneficiary verification notification: {e}")


def notify_beneficiary_rejected(beneficiary, rejection_reason: str) -> None:
    """
    Decoupled helper invoked when a beneficiary's verification is rejected.
    Sends notification to the campaign owner.
    """
    try:
        recipient = beneficiary.campaign.created_by
        create_notification(
            recipient=recipient,
            title="Beneficiary Verification Rejected",
            message=f"Beneficiary '{beneficiary.full_name}' for campaign '{beneficiary.campaign.title}' was rejected. Reason: {rejection_reason}",
            notification_type=NotificationType.BENEFICIARY_REJECTED,
            action_url=f"/beneficiaries/{beneficiary.id}/",
        )
    except Exception as e:
        logger.error(f"Failed to dispatch beneficiary rejection notification: {e}")


def notify_beneficiary_deleted(beneficiary) -> None:
    """
    Placeholder decoupled helper for beneficiary soft delete events.
    Can be used for analytical or sync signals.
    """
    pass
