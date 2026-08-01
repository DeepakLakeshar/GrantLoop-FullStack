import uuid
from django.conf import settings
from django.db import models


class NotificationType(models.TextChoices):
    CAMPAIGN_UPDATE = "campaign_update", "Campaign Update"
    DONATION_RECEIVED = "donation_received", "Donation Received"
    MILESTONE_REACHED = "milestone_reached", "Milestone Reached"
    PAYOUT_REQUESTED = "payout_requested", "Payout Requested"
    PAYOUT_APPROVED = "payout_approved", "Payout Approved"
    PAYOUT_REJECTED = "payout_rejected", "Payout Rejected"
    PAYOUT_PROCESSING = "payout_processing", "Payout Processing"
    PAYOUT_COMPLETED = "payout_completed", "Payout Completed"
    PAYOUT_FAILED = "payout_failed", "Payout Failed"
    PAYOUT_CANCELLED = "payout_cancelled", "Payout Cancelled"
    BENEFICIARY_VERIFIED = "beneficiary_verified", "Beneficiary Verified"
    BENEFICIARY_REJECTED = "beneficiary_rejected", "Beneficiary Rejected"
    GENERAL = "general", "General Notification"


class Notification(models.Model):
    """
    In-app Notification instance representing standard user notifications
    about platform lifecycle states (e.g. donations, payouts, milestone details).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        default=NotificationType.GENERAL,
        db_index=True,
    )
    action_url = models.URLField(max_length=500, blank=True, null=True)
    is_read = models.BooleanField(default=False, db_index=True)
    is_deleted = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "is_deleted", "is_read", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.recipient.email} - {self.title} ({self.notification_type})"
