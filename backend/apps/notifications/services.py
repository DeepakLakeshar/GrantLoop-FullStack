from django.db import transaction
from .models import Notification


def get_notification(*, notification_id) -> Notification:
    """
    Retrieves a single Notification by its UUID primary key,
    pre-fetching the recipient user.
    """
    return Notification.objects.select_related("recipient").get(id=notification_id)


def list_notifications(*, user):
    """
    Retrieves all non-deleted notifications for a specific user,
    ordered by newest first.
    """
    return Notification.objects.filter(recipient=user, is_deleted=False).select_related("recipient").order_by("-created_at")


def count_unread_notifications(*, user) -> int:
    """
    Counts all unread, non-deleted notifications for a specific user.
    """
    return Notification.objects.filter(recipient=user, is_read=False, is_deleted=False).count()


def create_notification(
    *,
    recipient,
    title: str,
    message: str,
    notification_type: str,
    action_url: str = None,
) -> Notification:
    """
    Creates and saves a single notification instance for a user.
    """
    valid_types = [choice[0] for choice in Notification.NOTIFICATION_TYPE_CHOICES]
    if notification_type not in valid_types:
        raise ValueError(f"Invalid notification type: {notification_type}")

    return Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        notification_type=notification_type,
        action_url=action_url,
    )


def create_notifications(
    *,
    recipients,
    title: str,
    message: str,
    notification_type: str,
    action_url: str = None,
) -> list[Notification]:
    """
    Bulk creates identical notifications for a list of recipient users.
    Optimized to query and insert in a single database round-trip.
    """
    valid_types = [choice[0] for choice in Notification.NOTIFICATION_TYPE_CHOICES]
    if notification_type not in valid_types:
        raise ValueError(f"Invalid notification type: {notification_type}")

    notifications = [
        Notification(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=notification_type,
            action_url=action_url,
        )
        for recipient in recipients
    ]

    with transaction.atomic():
        return Notification.objects.bulk_create(notifications)


def mark_as_read(*, notification: Notification) -> Notification:
    """
    Marks a single notification as read.
    """
    if not notification.is_read:
        notification.is_read = True
        notification.save(update_fields=["is_read", "updated_at"])
    return notification


def mark_all_as_read(*, user) -> int:
    """
    Marks all unread, non-deleted notifications for a specific user as read.
    Returns the count of updated records.
    """
    with transaction.atomic():
        unread = Notification.objects.filter(recipient=user, is_read=False, is_deleted=False)
        updated_count = unread.update(is_read=True)
    return updated_count
