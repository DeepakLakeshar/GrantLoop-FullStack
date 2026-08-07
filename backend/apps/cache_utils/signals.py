"""
Automatic signal-driven cache invalidation hooks for core GrantLoop domain models.
Neutralizes schema coupling and business logic duplication while guaranteeing cache coherency on mutations.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.cache_utils.keys import (
    NAMESPACE_ANALYTICS,
    NAMESPACE_BENEFICIARIES,
    NAMESPACE_CAMPAIGNS,
    NAMESPACE_DASHBOARD,
    NAMESPACE_LEADERBOARDS,
    NAMESPACE_MILESTONES,
    NAMESPACE_NOTIFICATIONS,
    NAMESPACE_PARTNERS,
    NAMESPACE_PAYOUTS,
    NAMESPACE_REPORTS,
)
from apps.cache_utils.services import CacheService


@receiver([post_save, post_delete], sender="campaigns.Campaign")
def invalidate_campaign_caches(sender, instance, **kwargs):
    CacheService.invalidate_namespace(NAMESPACE_CAMPAIGNS)
    CacheService.invalidate_namespace(NAMESPACE_DASHBOARD)
    CacheService.invalidate_namespace(NAMESPACE_LEADERBOARDS)
    CacheService.invalidate_namespace(NAMESPACE_REPORTS)
    if hasattr(instance, "pk") and instance.pk:
        CacheService.invalidate_object(NAMESPACE_CAMPAIGNS, f"detail:{instance.pk}")


@receiver([post_save, post_delete], sender="donations.Donation")
def invalidate_donation_caches(sender, instance, **kwargs):
    CacheService.invalidate_namespace(NAMESPACE_CAMPAIGNS)
    CacheService.invalidate_namespace(NAMESPACE_ANALYTICS)
    CacheService.invalidate_namespace(NAMESPACE_DASHBOARD)
    CacheService.invalidate_namespace(NAMESPACE_LEADERBOARDS)
    CacheService.invalidate_namespace(NAMESPACE_REPORTS)


@receiver([post_save, post_delete], sender="payouts.Payout")
def invalidate_payout_caches(sender, instance, **kwargs):
    CacheService.invalidate_namespace(NAMESPACE_PAYOUTS)
    CacheService.invalidate_namespace(NAMESPACE_DASHBOARD)
    CacheService.invalidate_namespace(NAMESPACE_REPORTS)
    CacheService.invalidate_namespace(NAMESPACE_ANALYTICS)


@receiver([post_save, post_delete], sender="beneficiaries.Beneficiary")
def invalidate_beneficiary_caches(sender, instance, **kwargs):
    CacheService.invalidate_namespace(NAMESPACE_BENEFICIARIES)
    CacheService.invalidate_namespace(NAMESPACE_DASHBOARD)
    CacheService.invalidate_namespace(NAMESPACE_REPORTS)


@receiver([post_save, post_delete], sender="milestones.Milestone")
def invalidate_milestone_caches(sender, instance, **kwargs):
    CacheService.invalidate_namespace(NAMESPACE_MILESTONES)
    CacheService.invalidate_namespace(NAMESPACE_CAMPAIGNS)
    CacheService.invalidate_namespace(NAMESPACE_DASHBOARD)


@receiver([post_save, post_delete], sender="notifications.Notification")
def invalidate_notification_caches(sender, instance, **kwargs):
    CacheService.invalidate_namespace(NAMESPACE_NOTIFICATIONS)
    if hasattr(instance, "recipient_id") and instance.recipient_id:
        CacheService.invalidate_object(NAMESPACE_NOTIFICATIONS, f"list:{instance.recipient_id}")


@receiver([post_save, post_delete], sender="execution_partners.ExecutionPartner")
def invalidate_partner_caches(sender, instance, **kwargs):
    CacheService.invalidate_namespace(NAMESPACE_PARTNERS)
    CacheService.invalidate_namespace(NAMESPACE_DASHBOARD)
    CacheService.invalidate_namespace(NAMESPACE_REPORTS)
