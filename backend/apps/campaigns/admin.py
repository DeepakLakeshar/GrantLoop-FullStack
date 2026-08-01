from django.contrib import admin

from .models import Beneficiary, Campaign, Category, TransparencyLog, Verification


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ["title", "status", "category", "created_by", "goal_amount", "raised_amount", "created_at"]
    list_filter = ["status", "category"]
    search_fields = ["title", "created_by__email", "created_by__full_name"]


@admin.register(Beneficiary)
class BeneficiaryAdmin(admin.ModelAdmin):
    list_display = ["name", "campaign", "verification_status"]
    list_filter = ["verification_status"]


@admin.register(Verification)
class VerificationAdmin(admin.ModelAdmin):
    list_display = ["campaign", "status", "verified_by", "created_at"]
    list_filter = ["status"]


@admin.register(TransparencyLog)
class TransparencyLogAdmin(admin.ModelAdmin):
    list_display = ["campaign", "action", "timestamp"]
    readonly_fields = ["id", "campaign", "action", "timestamp"]

    def has_add_permission(self, request):
        return False  # system-generated only, per models.py docstring
