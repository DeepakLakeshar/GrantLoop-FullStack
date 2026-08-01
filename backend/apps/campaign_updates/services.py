from django.core.exceptions import PermissionDenied
from django.db import transaction

from apps.campaigns.models import TransparencyLog

from .models import CampaignUpdate


def _can_manage_updates(*, campaign, actor) -> bool:
    if actor.role == "admin":
        return True
    return actor.role == "ngo" and campaign.created_by_id == actor.id


def create_update(*, campaign, actor, **fields) -> CampaignUpdate:
    if not _can_manage_updates(campaign=campaign, actor=actor):
        raise PermissionDenied("You don't have permission to post updates for this campaign.")

    with transaction.atomic():
        update = CampaignUpdate.objects.create(campaign=campaign, posted_by=actor, **fields)
        TransparencyLog.objects.create(
            campaign=campaign,
            action=f"Update posted: {update.get_update_type_display()}",
        )
    return update


def delete_update(*, update: CampaignUpdate, actor) -> None:
    if not _can_manage_updates(campaign=update.campaign, actor=actor):
        raise PermissionDenied("You don't have permission to delete this update.")
    update.delete()
