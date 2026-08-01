from rest_framework import serializers

from .models import CampaignUpdate


class CampaignUpdateSerializer(serializers.ModelSerializer):
    posted_by_name = serializers.CharField(source="posted_by.full_name", read_only=True)

    class Meta:
        model = CampaignUpdate
        fields = [
            "id", "campaign", "milestone", "posted_by", "posted_by_name",
            "update_type", "content", "image_url", "created_at",
        ]
        read_only_fields = ["id", "posted_by", "posted_by_name", "created_at"]

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError("Update content cannot be empty.")
        return value
