from rest_framework import serializers

from apps.accounts.serializers import UserPublicSerializer
from .models import NGOProfile


class NGOProfileSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)

    class Meta:
        model = NGOProfile
        fields = ["id", "user", "organization_name", "description", "logo_url", "website_url"]
        read_only_fields = ["id", "user"]


class NGOProfileWriteSerializer(serializers.ModelSerializer):
    """Separate from the read serializer since `user` must never be
    client-settable — it's always the requesting NGO, set in the view."""

    class Meta:
        model = NGOProfile
        fields = ["organization_name", "description", "logo_url", "website_url"]
