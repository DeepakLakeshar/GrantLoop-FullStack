import uuid

from django.conf import settings
from django.db import models


class Donation(models.Model):
    """
    Tracks financial contributions made by donors to specific campaigns.
    Supports multi-currency checkouts while recording settled values for
    campaign targets, and stores payment gateway reference IDs to handle
    signature webhooks asynchronously.
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="donations",
    )
    campaign = models.ForeignKey(
        "campaigns.Campaign",
        on_delete=models.PROTECT,
        related_name="donations",
    )
    original_amount = models.DecimalField(max_digits=12, decimal_places=2)
    original_currency = models.CharField(max_length=3)
    settled_amount = models.DecimalField(max_digits=12, decimal_places=2)
    settled_currency = models.CharField(max_length=3)
    is_anonymous = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        db_index=True,
    )
    gateway_type = models.CharField(max_length=30)
    gateway_order_id = models.CharField(max_length=255, unique=True)
    gateway_transaction_id = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        null=True,
    )
    receipt_url = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["campaign", "status"]),
            models.Index(fields=["donor"]),
            models.Index(fields=["created_at"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(original_amount__gt=0),
                name="donation_original_amount_gt_0",
            ),
            models.CheckConstraint(
                check=models.Q(settled_amount__gte=0),
                name="donation_settled_amount_gte_0",
            ),
        ]

    def __str__(self) -> str:
        donor_str = "Anonymous" if self.is_anonymous else (self.donor.full_name if self.donor else "Guest")
        return f"Donation {self.id} - {self.original_amount} {self.original_currency} by {donor_str}"
