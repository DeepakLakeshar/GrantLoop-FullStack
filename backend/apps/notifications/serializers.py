from rest_framework import serializers

from apps.accounts.serializers import UserPublicSerializer
from .models import Notification


class NotificationListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for displaying lists of notifications.
    Omit raw messages to keep payload small.
    """

    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "notification_type",
            "action_url",
            "is_read",
            "created_at",
        ]
        read_only_fields = fields


class NotificationDetailSerializer(serializers.ModelSerializer):
    """
    Detailed representation of a user notification.
    """

    recipient = UserPublicSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "recipient",
            "title",
            "message",
            "notification_type",
            "action_url",
            "is_read",
            "is_deleted",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields
