import uuid

from django.db import models

from apps.campaigns.models import Campaign


class Milestone(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In progress"),
        ("completed", "Completed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # PROTECT: same money-movement rule as everywhere else in this
    # project — released_amount tracks real fund movement, so this row
    # must survive campaign archival.
    campaign = models.ForeignKey(Campaign, on_delete=models.PROTECT, related_name="milestones")
    # ExecutionPartner connects to Campaign ONLY through this field —
    # never a direct FK (Architecture Freeze v1.0). String reference
    # avoids a direct cross-app import.
    execution_partner = models.ForeignKey(
        "execution_partners.ExecutionPartner",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="milestones",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    released_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    order = models.PositiveIntegerField(default=0)
    deadline = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["campaign", "order", "deadline"]
        indexes = [models.Index(fields=["campaign", "status"])]
        constraints = [
            models.CheckConstraint(
                check=models.Q(released_amount__lte=models.F("target_amount")),
                name="milestone_released_lte_target",
            ),
            models.CheckConstraint(check=models.Q(target_amount__gt=0), name="milestone_target_gt_0"),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.campaign_id})"

    @property
    def completion_percentage(self) -> float:
        if self.target_amount == 0:
            return 0.0
        return round(float(self.released_amount) / float(self.target_amount) * 100, 1)