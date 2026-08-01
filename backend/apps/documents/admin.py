from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["document_type", "campaign", "milestone", "beneficiary", "status", "uploaded_by", "uploaded_at"]
    list_filter = ["status", "document_type"]
    search_fields = ["document_type"]
