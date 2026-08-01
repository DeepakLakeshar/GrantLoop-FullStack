from rest_framework import serializers

from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    file = serializers.FileField(write_only=True)

    class Meta:
        model = Document
        fields = [
            "id", "campaign", "milestone", "verification", "ngo", "beneficiary",
            "campaign_update", "document_type", "file", "file_url",
            "uploaded_by", "status", "verified_by", "uploaded_at",
        ]
        read_only_fields = ["id", "uploaded_by", "status", "verified_by", "uploaded_at", "file_url"]

    def get_file_url(self, obj) -> str | None:
        if not obj.file:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(obj.file.url) if request else obj.file.url


class DocumentReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["verified", "rejected"])
