from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Django Admin registration for the Notification model.
    """

    list_display = [
        "id",
        "recipient",
        "title",
        "notification_type",
        "is_read",
        "is_deleted",
        "created_at",
    ]
    list_filter = ["is_read", "is_deleted", "notification_type", "created_at"]
    search_fields = ["recipient__email", "recipient__full_name", "title"]
    ordering = ["-created_at"]
    readonly_fields = ["id", "created_at", "updated_at"]
    autocomplete_fields = ["recipient"]
