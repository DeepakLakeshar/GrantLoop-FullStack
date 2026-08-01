from django.contrib import admin

from .models import Donation


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    """
    Django Admin registration for the Donation model.
    Defines list layouts, search filters, autocomplete fields, and read-only records.
    """

    list_display = [
        "id",
        "campaign",
        "donor",
        "original_amount",
        "original_currency",
        "settled_amount",
        "settled_currency",
        "status",
        "gateway_type",
        "created_at",
    ]
    list_filter = ["status", "gateway_type", "is_anonymous", "created_at"]
    search_fields = [
        "gateway_order_id",
        "gateway_transaction_id",
        "donor__email",
        "donor__full_name",
        "campaign__title",
    ]
    ordering = ["-created_at"]
    readonly_fields = [
        "id",
        "gateway_order_id",
        "gateway_transaction_id",
        "created_at",
        "updated_at",
    ]
    autocomplete_fields = ["donor", "campaign"]
