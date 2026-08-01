import uuid

from django.conf import settings
from django.db import models


class ExecutionPartner(models.Model):
    """
    Frozen minimal schema only (Architecture Freeze v1.0), same shape as
    NGOProfile. No Campaign FK — connects to Campaign only indirectly,
    through Milestone.execution_partner. Do not add fields beyond this.
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("verified", "Verified"),
        ("suspended", "Suspended"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="execution_partner_profile"
    )
    organization = models.CharField(max_length=255, blank=True)
    verification_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    class Meta:
        indexes = [models.Index(fields=["verification_status"])]

    def __str__(self) -> str:
        return self.organization or str(self.user_id)