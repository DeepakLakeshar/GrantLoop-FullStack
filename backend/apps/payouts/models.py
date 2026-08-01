import uuid
from decimal import Decimal
from django.conf import settings
from django.db import models


class PayoutStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    PROCESSING = "processing", "Processing"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"


class PayoutQuerySet(models.QuerySet):
    def active(self):
        """
        Excludes soft-deleted payout requests.
        """
        return self.filter(is_deleted=False)


class PayoutManager(models.Manager):
    def get_queryset(self):
        """
        Default query manager auto-excluding soft-deleted rows.
        """
        return PayoutQuerySet(self.model, using=self._db).active()

    def all_with_deleted(self):
        """
        Exposes full dataset including soft-deleted items for administrative audit trails.
        """
        return PayoutQuerySet(self.model, using=self._db)


class Payout(models.Model):
    """
    Production-grade Payout request mapping to a verified campaign and NGO owner.
    Maintains financial audit snapshots, gateway reference tags, and state transition histories.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ngo = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="payouts_received",
    )
    campaign = models.ForeignKey(
        "campaigns.Campaign",
        on_delete=models.PROTECT,
        related_name="payouts",
    )
    requested_amount = models.DecimalField(max_digits=12, decimal_places=2)
    approved_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    available_balance_before = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    available_balance_after = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default="INR")
    status = models.CharField(
        max_length=20,
        choices=PayoutStatus.choices,
        default=PayoutStatus.PENDING,
        db_index=True,
    )
    request_notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="payout_requests_created",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payout_approvals",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    gateway_reference = models.CharField(max_length=255, blank=True)
    transfer_reference = models.CharField(max_length=255, blank=True)
    failure_reason = models.TextField(blank=True)
    is_deleted = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PayoutManager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["campaign", "status"]),
            models.Index(fields=["ngo", "status"]),
            models.Index(fields=["is_deleted", "status"]),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(requested_amount__gt=0), name="payout_requested_gt_0"),
            models.CheckConstraint(
                check=models.Q(approved_amount__gte=0) | models.Q(approved_amount__isnull=True),
                name="payout_approved_gte_0",
            ),
        ]

    def __str__(self) -> str:
        return f"Payout({self.id}) - {self.campaign.title}: {self.requested_amount} {self.currency} ({self.status})"
