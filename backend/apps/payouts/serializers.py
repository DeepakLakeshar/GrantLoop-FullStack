from decimal import Decimal
from rest_framework import serializers
from .models import Payout
from apps.campaigns.models import Campaign


class PayoutListSerializer(serializers.ModelSerializer):
    """
    Concise read-only representation for feed listing endpoints.
    """
    campaign_title = serializers.ReadOnlyField(source="campaign.title")
    ngo_email = serializers.ReadOnlyField(source="ngo.email")

    class Meta:
        model = Payout
        fields = [
            "id",
            "campaign",
            "campaign_title",
            "ngo",
            "ngo_email",
            "requested_amount",
            "approved_amount",
            "currency",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class PayoutDetailSerializer(serializers.ModelSerializer):
    """
    Exhaustive read-only representation for single item inspection,
    exposing balance audit trails, notes, and payment references.
    """
    campaign_title = serializers.ReadOnlyField(source="campaign.title")
    ngo_email = serializers.ReadOnlyField(source="ngo.email")
    requested_by_email = serializers.ReadOnlyField(source="requested_by.email")
    approved_by_email = serializers.ReadOnlyField(source="approved_by.email")

    class Meta:
        model = Payout
        fields = [
            "id",
            "campaign",
            "campaign_title",
            "ngo",
            "ngo_email",
            "requested_amount",
            "approved_amount",
            "available_balance_before",
            "available_balance_after",
            "currency",
            "status",
            "request_notes",
            "admin_notes",
            "requested_by",
            "requested_by_email",
            "approved_by",
            "approved_by_email",
            "approved_at",
            "gateway_reference",
            "transfer_reference",
            "failure_reason",
            "is_deleted",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class PayoutCreateSerializer(serializers.Serializer):
    """
    Input validator for initiating a fund withdrawal request.
    """
    campaign = serializers.PrimaryKeyRelatedField(queryset=Campaign.objects.all(), required=True)
    requested_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=True, min_value=Decimal("0.01"))
    currency = serializers.CharField(max_length=3, default="INR", required=False)
    request_notes = serializers.CharField(required=False, allow_blank=True, default="")


class PayoutApproveSerializer(serializers.Serializer):
    """
    Input validator for administrative approval transitions.
    """
    approved_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, min_value=Decimal("0.01"))
    admin_notes = serializers.CharField(required=False, allow_blank=True, default="")


class PayoutRejectSerializer(serializers.Serializer):
    """
    Input validator for administrative rejection transitions.
    """
    rejection_reason = serializers.CharField(required=False, allow_blank=True, default="")
    admin_notes = serializers.CharField(required=False, allow_blank=True, default="")


class PayoutProcessSerializer(serializers.Serializer):
    """
    Input validator for triggering payment provider disbursement transfers.
    """
    gateway_type = serializers.CharField(max_length=50, required=False, default="mock")
    account_reference = serializers.CharField(max_length=255, required=False, default="default_acct")


class PayoutCompleteSerializer(serializers.Serializer):
    """
    Input validator for confirming transfer settlement.
    """
    transfer_reference = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")


class PayoutFailSerializer(serializers.Serializer):
    """
    Input validator for recording failed gateway execution.
    """
    failure_reason = serializers.CharField(required=False, allow_blank=True, default="Transfer failed at payment gateway.")
