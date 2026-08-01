import uuid

from django.conf import settings
from django.db import models

from apps.campaigns.models import Campaign
from apps.milestones.models import Milestone


class CampaignUpdate(models.Model):
    UPDATE_TYPE_CHOICES = [
        ("progress", "Progress"),
        ("fund_usage", "Fund usage"),
        ("closure_report", "Closure report"),
    ]

    # Field shape matches the frozen schema / frontend CampaignUpdate type
    # exactly (Reconciliation v1.1) — no "title" or numeric "progress"
    # field, since those aren't part of the authoritative schema and
    # would diverge from the already-built frontend contract. "Multiple
    # images/files" is satisfied by combining this model's single
    # image_url (cover image) with apps.documents.Document.campaign_update
    # (multi-file attachments) — not by adding fields here.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # PROTECT: public-facing accountability content, referenced by
    # donors — same rule as everywhere else, never silently disappears.
    campaign = models.ForeignKey(Campaign, on_delete=models.PROTECT, related_name="updates")
    milestone = models.ForeignKey(
        Milestone, on_delete=models.SET_NULL, null=True, blank=True, related_name="updates"
    )
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="posted_updates")
    update_type = models.CharField(max_length=20, choices=UPDATE_TYPE_CHOICES, default="progress")
    content = models.TextField()
    image_url = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["campaign", "created_at"])]

    def __str__(self) -> str:
        return f"Update on {self.campaign_id} @ {self.created_at:%Y-%m-%d}"
