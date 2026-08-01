from decimal import Decimal
from rest_framework import serializers
from apps.campaigns.models import Campaign
from apps.donations.models import Donation
from apps.notifications.models import Notification
from apps.payouts.models import Payout


class RecentCampaignSerializer(serializers.ModelSerializer):
    """
    Concise representation of recently created campaigns for dashboard timelines.
    """
    creator_email = serializers.ReadOnlyField(source="created_by.email")
    category_name = serializers.ReadOnlyField(source="category.name", default="")

    class Meta:
        model = Campaign
        fields = [
            "id",
            "title",
            "status",
            "goal_amount",
            "raised_amount",
            "campaign_currency",
            "creator_email",
            "category_name",
            "created_at",
        ]
        read_only_fields = fields


class RecentDonationSerializer(serializers.ModelSerializer):
    """
    Concise representation of recently received donations for dashboard timelines.
    """
    campaign_title = serializers.ReadOnlyField(source="campaign.title")
    donor_email = serializers.ReadOnlyField(source="donor.email", default="Anonymous")

    class Meta:
        model = Donation
        fields = [
            "id",
            "campaign",
            "campaign_title",
            "donor",
            "donor_email",
            "settled_amount",
            "settled_currency",
            "status",
            "created_at",
        ]
        read_only_fields = fields


class RecentNotificationSerializer(serializers.ModelSerializer):
    """
    Concise representation of recent notification events.
    """
    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "message",
            "notification_type",
            "is_read",
            "created_at",
        ]
        read_only_fields = fields


class RecentPayoutSerializer(serializers.ModelSerializer):
    """
    Concise representation of recent payout requests for admin audit feeds.
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
        ]
        read_only_fields = fields


class AdminDashboardSerializer(serializers.Serializer):
    """
    Comprehensive platform aggregation statistics for platform administrators.
    """
    total_users = serializers.IntegerField(min_value=0)
    total_ngos = serializers.IntegerField(min_value=0)
    verified_ngos = serializers.IntegerField(min_value=0)
    pending_ngo_verifications = serializers.IntegerField(min_value=0)

    total_campaigns = serializers.IntegerField(min_value=0)
    draft_campaigns = serializers.IntegerField(min_value=0)
    pending_campaigns = serializers.IntegerField(min_value=0)
    live_campaigns = serializers.IntegerField(min_value=0)
    completed_campaigns = serializers.IntegerField(min_value=0)
    rejected_campaigns = serializers.IntegerField(min_value=0)

    total_donations = serializers.IntegerField(min_value=0)
    successful_donations = serializers.IntegerField(min_value=0)
    pending_donations = serializers.IntegerField(min_value=0)
    failed_donations = serializers.IntegerField(min_value=0)
    refunded_donations = serializers.IntegerField(min_value=0)

    total_donation_amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    average_donation = serializers.DecimalField(max_digits=14, decimal_places=2)
    largest_donation = serializers.DecimalField(max_digits=14, decimal_places=2)

    total_beneficiaries = serializers.IntegerField(min_value=0)
    verified_beneficiaries = serializers.IntegerField(min_value=0)
    pending_beneficiaries = serializers.IntegerField(min_value=0)
    rejected_beneficiaries = serializers.IntegerField(min_value=0)

    total_payout_requests = serializers.IntegerField(min_value=0)
    pending_payouts = serializers.IntegerField(min_value=0)
    approved_payouts = serializers.IntegerField(min_value=0)
    completed_payouts = serializers.IntegerField(min_value=0)
    failed_payouts = serializers.IntegerField(min_value=0)
    cancelled_payouts = serializers.IntegerField(min_value=0)

    total_paid_amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    platform_balance = serializers.DecimalField(max_digits=14, decimal_places=2)

    recent_campaigns = RecentCampaignSerializer(many=True)
    recent_donations = RecentDonationSerializer(many=True)
    recent_notifications = RecentNotificationSerializer(many=True)
    recent_payout_requests = RecentPayoutSerializer(many=True)


class NGODashboardSerializer(serializers.Serializer):
    """
    Role-scoped analytical statistics for campaign creators and NGO administrators.
    """
    my_campaigns = serializers.IntegerField(min_value=0)
    live_campaigns = serializers.IntegerField(min_value=0)
    completed_campaigns = serializers.IntegerField(min_value=0)

    total_raised = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_donations = serializers.IntegerField(min_value=0)
    average_donation = serializers.DecimalField(max_digits=14, decimal_places=2)
    pending_donations = serializers.IntegerField(min_value=0)
    successful_donations = serializers.IntegerField(min_value=0)

    beneficiaries = serializers.IntegerField(min_value=0)
    verified_beneficiaries = serializers.IntegerField(min_value=0)

    milestones = serializers.IntegerField(min_value=0)
    completed_milestones = serializers.IntegerField(min_value=0)
    execution_partners = serializers.IntegerField(min_value=0)

    pending_payouts = serializers.IntegerField(min_value=0)
    completed_payouts = serializers.IntegerField(min_value=0)
    available_balance = serializers.DecimalField(max_digits=14, decimal_places=2)

    funding_percentage = serializers.FloatField()
    completion_percentage = serializers.FloatField()

    recent_donations = RecentDonationSerializer(many=True)
    recent_notifications = RecentNotificationSerializer(many=True)


class DonorDashboardSerializer(serializers.Serializer):
    """
    Role-scoped analytical dashboard for contributors and individual donors.
    """
    total_donations = serializers.IntegerField(min_value=0)
    successful_donations = serializers.IntegerField(min_value=0)
    pending_donations = serializers.IntegerField(min_value=0)
    refunded_donations = serializers.IntegerField(min_value=0)

    total_amount_donated = serializers.DecimalField(max_digits=14, decimal_places=2)
    average_donation = serializers.DecimalField(max_digits=14, decimal_places=2)
    largest_donation = serializers.DecimalField(max_digits=14, decimal_places=2)
    campaigns_supported = serializers.IntegerField(min_value=0)

    recent_donations = RecentDonationSerializer(many=True)
    recent_notifications = RecentNotificationSerializer(many=True)


class ChartSerializer(serializers.Serializer):
    """
    Normalized monthly time-series datapoint suitable for front-end rendering (e.g. React Recharts/Chart.js).
    """
    month = serializers.CharField(max_length=10)
    value = serializers.FloatField()


class LeaderboardSerializer(serializers.Serializer):
    """
    Normalized representation for comparative leaderboard rankings.
    """
    rank = serializers.IntegerField(min_value=1, required=False, default=1)
    id = serializers.CharField(max_length=255)
    name = serializers.CharField(max_length=255)
    amount = serializers.DecimalField(max_digits=14, decimal_places=2, required=False, default=Decimal("0.00"))
    count = serializers.IntegerField(min_value=0, required=False, default=0)
