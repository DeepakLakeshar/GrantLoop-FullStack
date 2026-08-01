import uuid
from django.conf import settings
from django.db import models


class Notification(models.Model):
    """
    In-app Notification instance representing standard user notifications
    about platform lifecycle states (e.g. donations, payouts, milestone details).
    """

    NOTIFICATION_TYPE_CHOICES = [
        ("campaign_update", "Campaign Update"),
        ("donation_received", "Donation Received"),
        ("milestone_reached", "Milestone Reached"),
        ("payout_completed", "Payout Completed"),
        ("general", "General Notification"),
    ]

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
        choices=NOTIFICATION_TYPE_CHOICES,
        default="general",
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
