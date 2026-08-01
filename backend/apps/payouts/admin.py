from django.contrib import admin
from .models import Payout


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    """
    Administrative interface for Payout inspection and auditing.
    """

    list_display = (
        "id",
        "campaign",
        "ngo",
        "requested_amount",
        "approved_amount",
        "currency",
        "status",
        "created_at",
    )
    list_filter = ("status", "currency", "is_deleted", "created_at", "approved_at")
    search_fields = (
        "campaign__title",
        "ngo__email",
        "ngo__full_name",
        "gateway_reference",
        "transfer_reference",
        "request_notes",
        "admin_notes",
    )
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "approved_at",
        "requested_by",
        "available_balance_before",
        "available_balance_after",
    )
    autocomplete_fields = ["campaign", "ngo", "requested_by", "approved_by"]
