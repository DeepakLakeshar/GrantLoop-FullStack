import uuid
from django.conf import settings
from django.db import models

from apps.campaigns.models import Campaign
from .validators import (
    validate_phone_number,
    validate_date_of_birth,
    validate_government_id,
    validate_profile_image,
)


class VerificationStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    VERIFIED = "verified", "Verified"
    REJECTED = "rejected", "Rejected"


class BeneficiaryQuerySet(models.QuerySet):
    def active(self):
        """
        Filters out soft-deleted records.
        """
        return self.filter(is_deleted=False)


class BeneficiaryManager(models.Manager):
    def get_queryset(self):
        """
        Default query manager which auto-excludes soft-deleted entries.
        """
        return BeneficiaryQuerySet(self.model, using=self._db).active()

    def all_with_deleted(self):
        """
        Exposes full dataset including soft-deleted items for admin layers.
        """
        return BeneficiaryQuerySet(self.model, using=self._db)


class Beneficiary(models.Model):
    """
    Beneficiary profile mapping to a specific campaign, maintaining
    audit fields, soft delete behavior, and validators.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # PROTECT: prevents deletion of campaigns with active beneficiaries
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.PROTECT,
        related_name="beneficiary_records",
    )
    full_name = models.CharField(max_length=255)
    email = models.EmailField(db_index=True)
    phone_number = models.CharField(max_length=30, validators=[validate_phone_number])
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    date_of_birth = models.DateField(blank=True, null=True, validators=[validate_date_of_birth])
    government_id = models.CharField(max_length=100, unique=True, validators=[validate_government_id], null=True, blank=True)
    profile_photo = models.FileField(upload_to="beneficiaries/", null=True, blank=True, validators=[validate_profile_image])

    # Status & Audit Trail
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
        db_index=True,
    )
    rejection_reason = models.TextField(blank=True, null=True)

    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_beneficiaries",
    )
    verified_at = models.DateTimeField(null=True, blank=True)

    rejected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rejected_beneficiaries",
    )
    rejected_at = models.DateTimeField(null=True, blank=True)

    # Soft Delete
    is_deleted = models.BooleanField(default=False, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Custom Manager overrides
    objects = BeneficiaryManager()

    class Meta:
        ordering = ["-created_at"]
        db_table = "campaigns_beneficiary"  # Reuses existing database table
        verbose_name_plural = "beneficiaries"
        indexes = [
            models.Index(fields=["campaign"]),
            models.Index(fields=["verification_status"]),
        ]

    def __str__(self) -> str:
        return self.full_name
