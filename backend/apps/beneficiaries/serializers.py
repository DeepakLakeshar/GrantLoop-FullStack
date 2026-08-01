from rest_framework import serializers

from apps.accounts.serializers import UserPublicSerializer
from .models import Beneficiary
from .validators import (
    validate_phone_number,
    validate_date_of_birth,
    validate_government_id,
    validate_profile_image,
)


class BeneficiaryListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing beneficiaries.
    Excludes private identifiers such as government_id.
    """

    class Meta:
        model = Beneficiary
        fields = [
            "id",
            "full_name",
            "email",
            "phone_number",
            "verification_status",
            "created_at",
        ]
        read_only_fields = fields


class BeneficiaryDetailSerializer(serializers.ModelSerializer):
    """
    Exhaustive serializer exposing all properties of a beneficiary.
    Filters out government_id for non-authorized users.
    """

    campaign = serializers.SerializerMethodField()
    verified_by = UserPublicSerializer(read_only=True)
    rejected_by = UserPublicSerializer(read_only=True)

    class Meta:
        model = Beneficiary
        fields = [
            "id",
            "campaign",
            "full_name",
            "email",
            "phone_number",
            "address",
            "city",
            "state",
            "country",
            "postal_code",
            "date_of_birth",
            "government_id",
            "profile_photo",
            "verification_status",
            "rejection_reason",
            "verified_by",
            "verified_at",
            "rejected_by",
            "rejected_at",
            "is_deleted",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get("request")

        # Privacy policy gate: only owners of campaign and admins can inspect government_id
        if request and request.user:
            user = request.user
            is_admin = user.role == "admin"
            is_owner = user.role == "ngo" and instance.campaign.created_by_id == user.id
            if not (is_admin or is_owner):
                representation.pop("government_id", None)
        else:
            representation.pop("government_id", None)

        return representation

    def get_campaign(self, obj):
        from apps.campaigns.serializers import CampaignListSerializer
        return CampaignListSerializer(obj.campaign, context=self.context).data


class BeneficiaryWriteSerializer(serializers.ModelSerializer):
    """
    Serializer used for creating and updating beneficiary records.
    Validates field constraints via validators.py.
    """

    class Meta:
        model = Beneficiary
        fields = [
            "campaign",
            "full_name",
            "email",
            "phone_number",
            "address",
            "city",
            "state",
            "country",
            "postal_code",
            "date_of_birth",
            "government_id",
            "profile_photo",
        ]

    def validate_phone_number(self, value):
        validate_phone_number(value)
        return value

    def validate_date_of_birth(self, value):
        if value:
            validate_date_of_birth(value)
        return value

    def validate_government_id(self, value):
        validate_government_id(value)
        return value

    def validate_profile_photo(self, value):
        if value:
            validate_profile_image(value)
        return value


class BeneficiaryVerificationSerializer(serializers.Serializer):
    """
    Validates rejection rationale during status transition requests.
    """

    rejection_reason = serializers.CharField(required=False, allow_blank=True, max_length=1000)
