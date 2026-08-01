from decimal import Decimal
from rest_framework import serializers


class ReportMetadataSerializer(serializers.Serializer):
    """
    Standardized report metadata envelope schema.
    """
    generated_at = serializers.CharField()
    generated_by = serializers.CharField()
    filters_applied = serializers.DictField(child=serializers.CharField())
    total_records = serializers.IntegerField()
    report_version = serializers.CharField()


class DonationReportSerializer(serializers.Serializer):
    """
    Donation Report schema.
    """
    donation_id = serializers.UUIDField(source="id")
    campaign_title = serializers.CharField(source="campaign.title")
    donor_email = serializers.CharField(default="Anonymous")
    amount = serializers.DecimalField(max_digits=14, decimal_places=2, source="settled_amount")
    currency = serializers.CharField(source="settled_currency")
    status = serializers.CharField()
    gateway_order_id = serializers.CharField(allow_blank=True, allow_null=True)
    transaction_id = serializers.CharField(source="gateway_transaction_id", allow_blank=True, allow_null=True, default="")
    created_at = serializers.DateTimeField()


class CampaignReportSerializer(serializers.Serializer):
    """
    Campaign Report schema with performance-annotated counts.
    """
    campaign_id = serializers.UUIDField(source="id")
    title = serializers.CharField()
    ngo_email = serializers.CharField(source="created_by.email")
    goal_amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    raised_amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    progress_percentage = serializers.FloatField()
    beneficiaries_count = serializers.IntegerField()
    milestones_count = serializers.IntegerField()
    execution_partners_count = serializers.IntegerField()
    status = serializers.CharField()


class NGOReportSerializer(serializers.Serializer):
    """
    NGO Performance Report schema.
    """
    ngo_id = serializers.IntegerField(source="id")
    email = serializers.CharField()
    full_name = serializers.CharField(allow_blank=True, default="")
    campaign_count = serializers.IntegerField()
    raised_amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    beneficiary_count = serializers.IntegerField()
    payout_total_amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    verification_status = serializers.BooleanField(source="email_verified")


class BeneficiaryReportSerializer(serializers.Serializer):
    """
    Beneficiary Verification Report schema.
    """
    beneficiary_id = serializers.UUIDField(source="id")
    full_name = serializers.CharField()
    campaign_title = serializers.CharField(source="campaign.title")
    verification_status = serializers.CharField()
    verification_date = serializers.DateTimeField(source="updated_at")
    rejection_reason = serializers.CharField(allow_blank=True, allow_null=True, default="")


class PayoutReportSerializer(serializers.Serializer):
    """
    Payout Disbursement Report schema.
    """
    payout_id = serializers.UUIDField(source="id")
    campaign_title = serializers.CharField(source="campaign.title")
    amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    currency = serializers.CharField()
    status = serializers.CharField()
    gateway_reference = serializers.CharField(source="gateway_reference", allow_blank=True, allow_null=True, default="")
    approved_by_email = serializers.CharField(allow_blank=True, allow_null=True, default="")
    completed_date = serializers.DateTimeField(source="updated_at", allow_null=True)


class FinancialReportSerializer(serializers.Serializer):
    """
    System-wide accounting reconciliation report schema with explicit mathematical verification flag.
    """
    total_donations = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_refunds = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_payouts = serializers.DecimalField(max_digits=14, decimal_places=2)
    platform_balance = serializers.DecimalField(max_digits=14, decimal_places=2)
    revenue_summary = serializers.DictField()
    accounting_consistent = serializers.BooleanField()


class AuditLogReportSerializer(serializers.Serializer):
    """
    Immutable audit timeline report schema.
    """
    log_id = serializers.UUIDField(source="id")
    campaign_id = serializers.UUIDField()
    campaign_title = serializers.CharField(source="campaign.title")
    action = serializers.CharField()
    timestamp = serializers.DateTimeField()
