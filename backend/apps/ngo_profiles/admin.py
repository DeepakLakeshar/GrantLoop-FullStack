from django.contrib import admin

from .models import NGOProfile


@admin.register(NGOProfile)
class NGOProfileAdmin(admin.ModelAdmin):
    list_display = ["organization_name", "user", "website_url"]
    search_fields = ["organization_name", "user__email"]
