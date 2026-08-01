from django.contrib import admin

from .models import ExecutionPartner


@admin.register(ExecutionPartner)
class ExecutionPartnerAdmin(admin.ModelAdmin):
    list_display = (
        "organization",
        "user",
        "verification_status",
    )

    list_filter = (
        "verification_status",
    )

    search_fields = (
        "organization",
        "user__full_name",
        "user__email",
    )

    ordering = (
        "organization",
    )

    readonly_fields = (
        "id",
    )

    list_select_related = (
        "user",
    )