from rest_framework import serializers

from apps.accounts.serializers import UserPublicSerializer
from apps.campaigns.serializers import CampaignListSerializer
from .models import Donation


class DonationListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing donation instances.
    Nests Campaign listings and masks anonymous donors.
    """

    donor = serializers.SerializerMethodField()
    campaign = CampaignListSerializer(read_only=True)

    class Meta:
        model = Donation
        fields = [
            "id",
            "donor",
            "campaign",
            "original_amount",
            "original_currency",
            "settled_amount",
            "settled_currency",
            "is_anonymous",
            "status",
            "receipt_url",
            "created_at",
        ]
        read_only_fields = fields

    def get_donor(self, obj):
        if obj.is_anonymous or not obj.donor:
            return {
                "id": None,
                "username": "Anonymous Donor",
                "role": "donor",
            }
        return UserPublicSerializer(obj.donor).data


class DonationDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for viewing detailed donation transactions.
    Nests Campaign listings and masks anonymous donors.
    """

    donor = serializers.SerializerMethodField()
    campaign = CampaignListSerializer(read_only=True)

    class Meta:
        model = Donation
        fields = [
            "id",
            "donor",
            "campaign",
            "original_amount",
            "original_currency",
            "settled_amount",
            "settled_currency",
            "is_anonymous",
            "status",
            "receipt_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_donor(self, obj):
        if obj.is_anonymous or not obj.donor:
            return {
                "id": None,
                "username": "Anonymous Donor",
                "role": "donor",
            }
        return UserPublicSerializer(obj.donor).data


class DonationWriteSerializer(serializers.ModelSerializer):
    """
    Serializer for initiating a checkout donation session.
    Restricts write inputs strictly to payment preparation properties.
    """

    class Meta:
        model = Donation
        fields = [
            "id",
            "campaign",
            "original_amount",
            "original_currency",
            "is_anonymous",
        ]
        read_only_fields = ["id"]

    def validate_original_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("original_amount must be greater than zero.")
        return value
