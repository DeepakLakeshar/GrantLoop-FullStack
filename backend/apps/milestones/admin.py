from django.contrib import admin

from .models import Milestone


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ["title", "campaign", "status", "target_amount", "released_amount", "order", "deadline"]
    list_filter = ["status"]
    search_fields = ["title", "campaign__title"]
    ordering = ["campaign", "order"]
