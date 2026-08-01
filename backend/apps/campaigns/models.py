import uuid

from django.conf import settings
from django.db import models


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Campaign(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("pending_verification", "Pending verification"),
        ("live", "Live"),
        ("completed", "Completed"),
        ("rejected", "Rejected"),
        ("archived", "Archived"),  # soft-delete state — see Meta note below
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    goal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    raised_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    campaign_currency = models.CharField(max_length=3, default="INR")  # ISO 4217
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="draft", db_index=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="campaigns", null=True, blank=True)
    location_city = models.CharField(max_length=100, blank=True)
    location_country = models.CharField(max_length=2, blank=True)  # ISO 3166-1 alpha-2
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)  # nullable: ongoing/evergreen campaigns are valid
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="campaigns"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Campaign is never hard-deleted (Architecture Freeze v1.0): every
        # money-movement/audit table PROTECTs its campaign FK, so deletion
        # would be blocked anyway once real history exists. "archived" is
        # the only supported deletion path.
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_by"]),
            models.Index(fields=["status", "created_at"]),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(raised_amount__gte=0), name="campaign_raised_gte_0"),
            models.CheckConstraint(check=models.Q(goal_amount__gt=0), name="campaign_goal_gt_0"),
        ]

    def __str__(self) -> str:
        return self.title

    @property
    def funding_percentage(self) -> float:
        if self.goal_amount == 0:
            return 0.0
        return round(float(self.raised_amount) / float(self.goal_amount) * 100, 1)


class Verification(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("more_info_requested", "More info requested"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # PROTECT: verification decisions are compliance-relevant audit
    # records and must survive campaign archival.
    campaign = models.ForeignKey(Campaign, on_delete=models.PROTECT, related_name="verifications")
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="verifications_done"
    )
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="pending")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [models.Index(fields=["campaign", "status"])]

    def __str__(self) -> str:
        return f"Verification({self.campaign_id}, {self.status})"


class TransparencyLog(models.Model):
    """Public, append-only, campaign-scoped timeline. Written exclusively
    by the service layer (see services.py) on state-changing actions —
    never directly writable via the API by any role, including admin."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(Campaign, on_delete=models.PROTECT, related_name="transparency_logs")
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]
        indexes = [models.Index(fields=["campaign", "timestamp"])]

    def __str__(self) -> str:
        return f"{self.campaign_id} - {self.action}"
