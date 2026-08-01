import uuid

from django.conf import settings
from django.db import models

from apps.campaigns.models import Beneficiary, Campaign, Verification
from apps.campaign_updates.models import CampaignUpdate
from apps.milestones.models import Milestone

# Suggested types, not an enforced enum — document_type is a plain string
# field by design (Reconciliation v1.1: "a new type never needs a
# migration"). This list is used for soft validation/UI hints only.
SUGGESTED_DOCUMENT_TYPES = [
    "photo", "invoice", "certificate", "completion_report",
    "inspection_report", "government_id", "proof_document", "other",
]


class Document(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("verified", "Verified"),
        ("rejected", "Rejected"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Exactly one of these six should be set per row — validated in
    # services.py, not a DB constraint (a CHECK across six nullable FKs
    # gets unreadable fast; a service-layer validator is the established
    # pattern here, same reasoning recorded when this model was first
    # designed). All six use PROTECT, not CASCADE — Document is evidence,
    # and evidence should never silently vanish because something it's
    # attached to was deleted, consistent with every other evidence/audit
    # table in this project.
    campaign = models.ForeignKey(Campaign, on_delete=models.PROTECT, null=True, blank=True, related_name="documents")
    milestone = models.ForeignKey(Milestone, on_delete=models.PROTECT, null=True, blank=True, related_name="documents")
    verification = models.ForeignKey(Verification, on_delete=models.PROTECT, null=True, blank=True, related_name="documents")
    ngo = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="ngo_documents")
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.PROTECT, null=True, blank=True, related_name="documents")
    campaign_update = models.ForeignKey(CampaignUpdate, on_delete=models.PROTECT, null=True, blank=True, related_name="documents")

    document_type = models.CharField(max_length=50)
    # Local storage for this phase (no AWS credentials in this
    # environment) — production swaps to django-storages/S3 per
    # Architecture Freeze v1.0's infrastructure section via a settings
    # change only; nothing here needs to change shape for that swap.
    file = models.FileField(upload_to="documents/%Y/%m/")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="uploaded_documents")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="verified_documents"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]
        indexes = [
            models.Index(fields=["campaign"]),
            models.Index(fields=["milestone"]),
            models.Index(fields=["beneficiary"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"{self.document_type} ({self.id})"

    @property
    def is_sensitive(self) -> bool:
        """Beneficiary-scoped documents (e.g. government ID) are personal
        data, not public evidence — flagged here so the view layer can
        keep them out of public listings. Everything else (campaign,
        milestone, campaign_update, verification-support evidence) is
        public accountability material by design."""
        return self.beneficiary_id is not None
