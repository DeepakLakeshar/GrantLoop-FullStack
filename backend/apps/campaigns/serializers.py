from rest_framework import serializers

from apps.accounts.serializers import UserPublicSerializer
from .models import Campaign, Category, TransparencyLog, Verification
from apps.beneficiaries.serializers import BeneficiaryListSerializer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]
        read_only_fields = fields


class VerificationSerializer(serializers.ModelSerializer):
    verified_by = UserPublicSerializer(read_only=True)

    class Meta:
        model = Verification
        fields = ["id", "campaign", "verified_by", "status", "notes", "created_at"]
        read_only_fields = ["id", "verified_by", "created_at"]


class TransparencyLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransparencyLog
        fields = ["id", "campaign", "action", "timestamp"]
        read_only_fields = fields  # system-generated only, see models.py docstring


class CampaignListSerializer(serializers.ModelSerializer):
    """Lightweight — used for Cause Listing. Deliberately does not nest
    beneficiaries/verifications/logs, matching the pattern already
    established on the frontend (CampaignListSerializer vs
    CampaignDetailSerializer) to avoid N+1 queries on the browse view."""

    funding_percentage = serializers.ReadOnlyField()
    created_by = UserPublicSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Campaign
        fields = [
            "id", "title", "goal_amount", "raised_amount", "campaign_currency",
            "funding_percentage", "status", "category", "location_city",
            "location_country", "start_date", "end_date", "created_by", "created_at",
        ]
        read_only_fields = fields


class CampaignDetailSerializer(serializers.ModelSerializer):
    funding_percentage = serializers.ReadOnlyField()
    created_by = UserPublicSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    beneficiaries = BeneficiaryListSerializer(many=True, read_only=True, source="beneficiary_records")
    latest_verification = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = [
            "id", "title", "description", "goal_amount", "raised_amount",
            "campaign_currency", "funding_percentage", "status", "category",
            "location_city", "location_country", "start_date", "end_date",
            "created_by", "created_at", "updated_at", "beneficiaries", "latest_verification",
        ]
        read_only_fields = fields

    def get_latest_verification(self, obj):
        verification = obj.verifications.order_by("-created_at").first()
        return VerificationSerializer(verification).data if verification else None


class CampaignWriteSerializer(serializers.ModelSerializer):
    """Create/update — deliberately narrow field set. status, raised_amount,
    and created_by are never client-writable; they change only through
    the service layer (submit/verify actions), never a direct PATCH."""

    class Meta:
        model = Campaign
        fields = [
            "id", "title", "description", "goal_amount", "campaign_currency",
            "category", "location_city", "location_country", "start_date", "end_date",
        ]
        read_only_fields = ["id"]

    def validate_goal_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("goal_amount must be greater than 0.")
        return value

    def validate(self, attrs):
        start = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end = attrs.get("end_date", getattr(self.instance, "end_date", None))
        if start and end and end < start:
            raise serializers.ValidationError("end_date cannot be before start_date.")
        return attrs
