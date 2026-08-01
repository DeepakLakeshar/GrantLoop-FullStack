"""
Business logic lives here, never in views/serializers (design principle
established in Architecture Freeze v1.0). Every state-changing action on
a Campaign goes through exactly one function here, and every one of them
writes the corresponding TransparencyLog entry — there is no other path
that mutates campaign status.
"""
from django.core.exceptions import PermissionDenied
from django.db import transaction

from .models import Campaign, TransparencyLog, Verification


def create_campaign(*, created_by, **fields) -> Campaign:
    return Campaign.objects.create(created_by=created_by, status="draft", **fields)


def submit_campaign_for_verification(*, campaign: Campaign, actor) -> Campaign:
    if campaign.created_by_id != actor.id and actor.role != "admin":
        raise PermissionDenied("Only the owning NGO or an admin can submit this campaign.")
    if campaign.status != "draft":
        raise ValueError(f"Cannot submit a campaign with status '{campaign.status}'.")

    with transaction.atomic():
        campaign.status = "pending_verification"
        campaign.save(update_fields=["status", "updated_at"])
        TransparencyLog.objects.create(campaign=campaign, action="Campaign submitted for verification")
    return campaign


def review_campaign(*, campaign: Campaign, reviewer, status: str, notes: str = "") -> Verification:
    """The institution/admin review action. Creates the Verification
    record AND transitions Campaign.status in one atomic operation —
    these two things are never allowed to happen independently."""
    if campaign.status != "pending_verification":
        raise ValueError(f"Cannot review a campaign with status '{campaign.status}'.")

    status_to_campaign_status = {
        "approved": "live",
        "rejected": "rejected",
        "more_info_requested": "pending_verification",  # stays put
    }
    if status not in status_to_campaign_status:
        raise ValueError(f"Invalid verification status '{status}'.")

    with transaction.atomic():
        verification = Verification.objects.create(
            campaign=campaign, verified_by=reviewer, status=status, notes=notes
        )
        new_campaign_status = status_to_campaign_status[status]
        if new_campaign_status != campaign.status:
            campaign.status = new_campaign_status
            campaign.save(update_fields=["status", "updated_at"])

        log_message = {
            "approved": "Campaign approved and is now live",
            "rejected": "Campaign rejected during verification",
            "more_info_requested": "Institution requested more information",
        }[status]
        TransparencyLog.objects.create(campaign=campaign, action=log_message)

    return verification


def archive_campaign(*, campaign: Campaign, actor) -> Campaign:
    """The only supported 'deletion' path (Architecture Freeze v1.0) —
    Campaign is never hard-deleted."""
    if actor.role != "admin":
        raise PermissionDenied("Only an admin can archive a campaign.")

    with transaction.atomic():
        campaign.status = "archived"
        campaign.save(update_fields=["status", "updated_at"])
        TransparencyLog.objects.create(campaign=campaign, action="Campaign archived")
    return campaign



