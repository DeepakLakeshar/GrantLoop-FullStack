import uuid

from django.conf import settings
from django.db import models


class NGOProfile(models.Model):
    """Mirrors ExecutionPartner's shape exactly (same established pattern
    from Architecture Reconciliation v1.1) — a public-facing profile for
    an NGO-role user, not a new design language."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ngo_profile"
    )
    organization_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    logo_url = models.URLField(max_length=500, blank=True)
    website_url = models.URLField(max_length=500, blank=True)

    def __str__(self) -> str:
        return self.organization_name
