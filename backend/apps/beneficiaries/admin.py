from django.contrib import admin
from .models import Beneficiary


@admin.register(Beneficiary)
class BeneficiaryAdmin(admin.ModelAdmin):
    """
    Django admin configuration class for Beneficiaries.
    Uses all_with_deleted manager to inspect soft-deleted records.
    """

    list_display = [
        "id",
        "full_name",
        "email",
        "phone_number",
        "verification_status",
        "is_deleted",
        "created_at",
    ]
    list_filter = ["verification_status", "is_deleted", "created_at"]
    search_fields = ["full_name", "email", "phone_number", "government_id"]
    ordering = ["-created_at"]
    readonly_fields = [
        "id",
        "verified_by",
        "verified_at",
        "rejected_by",
        "rejected_at",
        "created_at",
        "updated_at",
    ]
    autocomplete_fields = ["campaign", "verified_by", "rejected_by"]

    def get_queryset(self, request):
        """
        Ensure the admin list displays all items including soft-deleted ones.
        """
        return Beneficiary.objects.all_with_deleted()
