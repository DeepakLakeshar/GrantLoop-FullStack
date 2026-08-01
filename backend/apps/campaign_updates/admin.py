from django.contrib import admin

from .models import CampaignUpdate


@admin.register(CampaignUpdate)
class CampaignUpdateAdmin(admin.ModelAdmin):
    list_display = ["campaign", "update_type", "posted_by", "created_at"]
    list_filter = ["update_type"]
    search_fields = ["campaign__title", "content"]
