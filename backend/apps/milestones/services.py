"""
Business logic lives here, never in views/serializers — same convention
as apps.campaigns.services. Every status transition writes a
TransparencyLog entry on the parent campaign, consistent with how
campaign-level lifecycle events are already logged.
"""
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils import timezone

from apps.campaigns.models import TransparencyLog

from .models import Milestone

VALID_TRANSITIONS = {
    "pending": {"in_progress"},
    "in_progress": {"completed"},
    "completed": set(),
}


def _can_manage_milestone(*, campaign, actor) -> bool:
    if actor.role == "admin":
        return True
    if actor.role == "institution":
        return True
    return actor.role == "ngo" and campaign.created_by_id == actor.id


def create_milestone(*, campaign, actor, **fields) -> Milestone:
    if not _can_manage_milestone(campaign=campaign, actor=actor):
        raise PermissionDenied("You don't have permission to add milestones to this campaign.")

    with transaction.atomic():
        milestone = Milestone.objects.create(campaign=campaign, **fields)
        TransparencyLog.objects.create(
            campaign=campaign, action=f"Milestone '{milestone.title}' created"
        )
    return milestone


def reorder_milestones(*, campaign, actor, ordered_ids: list[str]) -> list[Milestone]:
    if not _can_manage_milestone(campaign=campaign, actor=actor):
        raise PermissionDenied("You don't have permission to reorder milestones on this campaign.")

    milestones = {str(m.id): m for m in Milestone.objects.filter(campaign=campaign)}
    if set(ordered_ids) != set(milestones.keys()):
        raise ValueError("ordered_ids must contain exactly the campaign's existing milestone ids.")

    with transaction.atomic():
        for index, milestone_id in enumerate(ordered_ids):
            milestone = milestones[milestone_id]
            if milestone.order != index:
                milestone.order = index
                milestone.save(update_fields=["order"])

    return list(Milestone.objects.filter(campaign=campaign).order_by("order"))


def transition_status(*, milestone: Milestone, actor, new_status: str) -> Milestone:
    if not _can_manage_milestone(campaign=milestone.campaign, actor=actor):
        raise PermissionDenied("You don't have permission to update this milestone.")

    allowed_next = VALID_TRANSITIONS.get(milestone.status, set())
    if new_status not in allowed_next:
        raise ValueError(
            f"Cannot transition milestone from '{milestone.status}' to '{new_status}'."
        )

    with transaction.atomic():
        milestone.status = new_status
        if new_status == "completed":
            milestone.completed_at = timezone.now()
            milestone.save(update_fields=["status", "completed_at"])
        else:
            milestone.save(update_fields=["status"])

        TransparencyLog.objects.create(
            campaign=milestone.campaign,
            action=f"Milestone '{milestone.title}' moved to {new_status.replace('_', ' ')}",
        )
    return milestone
