from decimal import Decimal
from typing import Any, Dict, List, Optional
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Count, Sum, Avg, Min, Max, F, Case, When, Value, Q, Exists, OuterRef, ExpressionWrapper
from django.db.models.functions import Coalesce, ExtractMonth
from django.core.exceptions import PermissionDenied

from apps.campaigns.models import Campaign
from apps.donations.models import Donation
from apps.notifications.models import Notification
from apps.beneficiaries.models import Beneficiary
from apps.payouts.models import Payout
from apps.milestones.models import Milestone
from apps.execution_partners.models import ExecutionPartner
from apps.payouts.services import get_available_balance as get_campaign_available_balance

User = get_user_model()

MONTH_MAP = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
}


def apply_analytics_filters(
    qs: models.QuerySet,
    params: Dict[str, Any],
    *,
    date_field: str = "created_at",
    status_field: Optional[str] = "status",
    campaign_field: Optional[str] = None,
    ngo_field: Optional[str] = None,
    search_fields: Optional[List[str]] = None,
) -> models.QuerySet:
    """
    Generic query filter application avoiding repeated ORM filtering patterns.
    Safely applies chronological, relational, status, and full-text search parameters.
    """
    if not params:
        return qs

    year = params.get("year")
    if year:
        try:
            qs = qs.filter(**{f"{date_field}__year": int(year)})
        except (ValueError, TypeError):
            pass

    month = params.get("month")
    if month:
        try:
            qs = qs.filter(**{f"{date_field}__month": int(month)})
        except (ValueError, TypeError):
            pass

    status = params.get("status")
    if status and status_field:
        qs = qs.filter(**{status_field: status})

    campaign = params.get("campaign")
    if campaign and campaign_field:
        qs = qs.filter(**{campaign_field: campaign})

    ngo = params.get("ngo")
    if ngo and ngo_field:
        qs = qs.filter(**{ngo_field: ngo})

    query = params.get("search")
    if query and search_fields:
        q_obj = models.Q()
        for field in search_fields:
            q_obj |= models.Q(**{f"{field}__icontains": query})
        qs = qs.filter(q_obj)

    return qs


def get_admin_dashboard(params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Computes platform-wide aggregated telemetry for administrative overviews.
    Uses conditional Case/When aggregations to compute multi-status counts in single DB queries
    to completely eliminate N+1 latency.
    """
    params = params or {}
    users_qs = apply_analytics_filters(User.objects.all(), params, date_field="date_joined", status_field=None)
    campaigns_qs = apply_analytics_filters(
        Campaign.objects.all(),
        params,
        search_fields=["title", "created_by__full_name", "created_by__email"],
    )
    donations_qs = apply_analytics_filters(
        Donation.objects.all(),
        params,
        campaign_field="campaign_id",
        ngo_field="campaign__created_by_id",
        search_fields=["campaign__title", "donor__email", "donor__full_name"],
    )
    beneficiaries_qs = apply_analytics_filters(
        Beneficiary.objects.filter(is_deleted=False),
        params,
        status_field="verification_status",
        campaign_field="campaign_id",
        ngo_field="campaign__created_by_id",
        search_fields=["full_name", "campaign__title"],
    )
    payouts_qs = apply_analytics_filters(
        Payout.objects.all_with_deleted(),
        params,
        campaign_field="campaign_id",
        ngo_field="ngo_id",
        search_fields=["campaign__title", "ngo__email"],
    )

    # 1. User & NGO metrics
    user_stats = users_qs.aggregate(
        total=Count("id"),
        total_ngos=Count(Case(When(role="ngo", then=1), output_field=models.IntegerField())),
        verified_ngos=Count(Case(When(role="ngo", email_verified=True, then=1), output_field=models.IntegerField())),
        pending_ngos=Count(Case(When(role="ngo", email_verified=False, then=1), output_field=models.IntegerField())),
    )

    # 2. Campaign metrics via conditional aggregation
    camp_stats = campaigns_qs.aggregate(
        total=Count("id"),
        draft=Count(Case(When(status="draft", then=1), output_field=models.IntegerField())),
        pending=Count(Case(When(status="pending_verification", then=1), output_field=models.IntegerField())),
        live=Count(Case(When(status="live", then=1), output_field=models.IntegerField())),
        completed=Count(Case(When(status="completed", then=1), output_field=models.IntegerField())),
        rejected=Count(Case(When(status="rejected", then=1), output_field=models.IntegerField())),
    )

    # 3. Donation metrics
    don_stats = donations_qs.aggregate(
        total_cnt=Count("id"),
        success_cnt=Count(Case(When(status="success", then=1), output_field=models.IntegerField())),
        pending_cnt=Count(Case(When(status="pending", then=1), output_field=models.IntegerField())),
        failed_cnt=Count(Case(When(status="failed", then=1), output_field=models.IntegerField())),
        refunded_cnt=Count(Case(When(status="refunded", then=1), output_field=models.IntegerField())),
        total_amt=Coalesce(Sum("settled_amount", filter=Q(status="success")), Value(0), output_field=models.DecimalField(max_digits=14, decimal_places=2)),
        avg_amt=Coalesce(Avg("settled_amount", filter=Q(status="success")), Value(0), output_field=models.DecimalField(max_digits=14, decimal_places=2)),
        max_amt=Coalesce(Max("settled_amount", filter=Q(status="success")), Value(0), output_field=models.DecimalField(max_digits=14, decimal_places=2)),
    )

    total_donation_amount = Decimal(str(don_stats["total_amt"] or "0.00"))
    average_donation = Decimal(str(don_stats["avg_amt"] or "0.00"))
    largest_donation = Decimal(str(don_stats["max_amt"] or "0.00"))

    # 4. Beneficiary metrics
    benef_stats = beneficiaries_qs.aggregate(
        total=Count("id"),
        verified=Count(Case(When(verification_status="verified", then=1), output_field=models.IntegerField())),
        pending=Count(Case(When(verification_status="pending", then=1), output_field=models.IntegerField())),
        rejected=Count(Case(When(verification_status="rejected", then=1), output_field=models.IntegerField())),
    )

    # 5. Payout metrics
    pay_stats = payouts_qs.aggregate(
        total_req=Count("id", filter=Q(is_deleted=False)),
        pending=Count(Case(When(is_deleted=False, status="pending", then=1), output_field=models.IntegerField())),
        approved=Count(Case(When(is_deleted=False, status="approved", then=1), output_field=models.IntegerField())),
        completed=Count(Case(When(is_deleted=False, status="completed", then=1), output_field=models.IntegerField())),
        failed=Count(Case(When(is_deleted=False, status="failed", then=1), output_field=models.IntegerField())),
        cancelled=Count(Case(When(status="cancelled", then=1), output_field=models.IntegerField())),
        total_paid=Coalesce(
            Sum(
                Case(
                    When(approved_amount__isnull=False, then=F("approved_amount")),
                    default=F("requested_amount"),
                    output_field=models.DecimalField(),
                ),
                filter=Q(is_deleted=False, status="completed"),
            ),
            Value(0),
            output_field=models.DecimalField(max_digits=14, decimal_places=2),
        ),
    )
    total_paid_amount = Decimal(str(pay_stats["total_paid"] or "0.00"))
    platform_balance = max(Decimal("0.00"), total_donation_amount - total_paid_amount)

    # 6. Recent timeline activities utilizing select_related/defer to optimize bandwidth
    recent_campaigns = list(
        campaigns_qs.select_related("category", "created_by").defer("description").order_by("-created_at")[:5]
    )
    recent_donations = list(
        donations_qs.select_related("campaign", "donor").order_by("-created_at")[:5]
    )
    recent_notifications = list(
        Notification.objects.select_related("recipient").order_by("-created_at")[:5]
    )
    recent_payouts = list(
        Payout.objects.select_related("campaign", "ngo", "requested_by", "approved_by").order_by("-created_at")[:5]
    )

    return {
        "total_users": user_stats["total"] or 0,
        "total_ngos": user_stats["total_ngos"] or 0,
        "verified_ngos": user_stats["verified_ngos"] or 0,
        "pending_ngo_verifications": user_stats["pending_ngos"] or 0,

        "total_campaigns": camp_stats["total"] or 0,
        "draft_campaigns": camp_stats["draft"] or 0,
        "pending_campaigns": camp_stats["pending"] or 0,
        "live_campaigns": camp_stats["live"] or 0,
        "completed_campaigns": camp_stats["completed"] or 0,
        "rejected_campaigns": camp_stats["rejected"] or 0,

        "total_donations": don_stats["total_cnt"] or 0,
        "successful_donations": don_stats["success_cnt"] or 0,
        "pending_donations": don_stats["pending_cnt"] or 0,
        "failed_donations": don_stats["failed_cnt"] or 0,
        "refunded_donations": don_stats["refunded_cnt"] or 0,
        "total_donation_amount": total_donation_amount,
        "average_donation": average_donation,
        "largest_donation": largest_donation,

        "total_beneficiaries": benef_stats["total"] or 0,
        "verified_beneficiaries": benef_stats["verified"] or 0,
        "pending_beneficiaries": benef_stats["pending"] or 0,
        "rejected_beneficiaries": benef_stats["rejected"] or 0,

        "total_payout_requests": pay_stats["total_req"] or 0,
        "pending_payouts": pay_stats["pending"] or 0,
        "approved_payouts": pay_stats["approved"] or 0,
        "completed_payouts": pay_stats["completed"] or 0,
        "failed_payouts": pay_stats["failed"] or 0,
        "cancelled_payouts": pay_stats["cancelled"] or 0,
        "total_paid_amount": total_paid_amount,
        "platform_balance": platform_balance,

        "recent_campaigns": recent_campaigns,
        "recent_donations": recent_donations,
        "recent_notifications": recent_notifications,
        "recent_payout_requests": recent_payouts,
    }


def get_ngo_dashboard(user, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Computes role-scoped analytics for an NGO user.
    Reuses payout available balance business service to guarantee computational adherence and zero duplication.
    """
    params = params or {}
    if getattr(user, "role", None) != "ngo":
        raise PermissionDenied("Only NGO users can access NGO analytics dashboard.")

    campaigns_qs = apply_analytics_filters(
        Campaign.objects.filter(created_by=user),
        params,
        search_fields=["title"],
    )
    donations_qs = apply_analytics_filters(
        Donation.objects.filter(campaign__created_by=user),
        params,
        campaign_field="campaign_id",
        search_fields=["campaign__title", "donor__email", "donor__full_name"],
    )
    beneficiaries_qs = apply_analytics_filters(
        Beneficiary.objects.filter(campaign__created_by=user, is_deleted=False),
        params,
        status_field="verification_status",
        campaign_field="campaign_id",
    )
    milestones_qs = apply_analytics_filters(
        Milestone.objects.filter(campaign__created_by=user),
        params,
        status_field="status",
        campaign_field="campaign_id",
    )
    payouts_qs = apply_analytics_filters(
        Payout.objects.filter(campaign__created_by=user, is_deleted=False),
        params,
        campaign_field="campaign_id",
    )

    camp_stats = campaigns_qs.aggregate(
        total=Count("id"),
        live=Count(Case(When(status="live", then=1), output_field=models.IntegerField())),
        completed=Count(Case(When(status="completed", then=1), output_field=models.IntegerField())),
        total_raised=Coalesce(Sum("raised_amount"), Value(0), output_field=models.DecimalField(max_digits=14, decimal_places=2)),
        total_goal=Coalesce(Sum("goal_amount"), Value(0), output_field=models.DecimalField(max_digits=14, decimal_places=2)),
    )

    don_stats = donations_qs.aggregate(
        total_cnt=Count("id", filter=Q(status="success")),
        pending_cnt=Count("id", filter=Q(status="pending")),
        success_cnt=Count("id", filter=Q(status="success")),
        avg_amt=Coalesce(Avg("settled_amount", filter=Q(status="success")), Value(0), output_field=models.DecimalField(max_digits=14, decimal_places=2)),
    )

    benef_stats = beneficiaries_qs.aggregate(
        total=Count("id"),
        verified=Count("id", filter=Q(verification_status="verified")),
    )

    mile_stats = milestones_qs.aggregate(
        total=Count("id"),
        completed=Count("id", filter=Q(status="completed")),
    )
    exec_partner_count = ExecutionPartner.objects.filter(milestones__campaign__created_by=user).distinct().count()

    pay_stats = payouts_qs.aggregate(
        pending=Count("id", filter=Q(status="pending")),
        completed=Count("id", filter=Q(status="completed")),
    )

    # Reuse service layer to compute exact available balance across live/completed campaigns
    active_campaigns = campaigns_qs.filter(status__in=["live", "completed"])
    available_bal = Decimal("0.00")
    for camp in active_campaigns:
        available_bal += get_campaign_available_balance(camp)

    total_raised = Decimal(str(camp_stats["total_raised"] or "0.00"))
    total_goal = Decimal(str(camp_stats["total_goal"] or "0.00"))
    funding_pct = round(float(total_raised) / float(total_goal) * 100, 1) if total_goal > Decimal("0.00") else 0.0

    m_total = mile_stats["total"] or 0
    m_comp = mile_stats["completed"] or 0
    completion_pct = round(float(m_comp) / float(m_total) * 100, 1) if m_total > 0 else 0.0

    recent_donations = list(donations_qs.select_related("campaign", "donor").order_by("-created_at")[:5])
    recent_notifications = list(Notification.objects.filter(recipient=user).order_by("-created_at")[:5])

    return {
        "my_campaigns": camp_stats["total"] or 0,
        "live_campaigns": camp_stats["live"] or 0,
        "completed_campaigns": camp_stats["completed"] or 0,

        "total_raised": total_raised,
        "total_donations": don_stats["total_cnt"] or 0,
        "average_donation": Decimal(str(don_stats["avg_amt"] or "0.00")),
        "pending_donations": don_stats["pending_cnt"] or 0,
        "successful_donations": don_stats["success_cnt"] or 0,

        "beneficiaries": benef_stats["total"] or 0,
        "verified_beneficiaries": benef_stats["verified"] or 0,

        "milestones": m_total,
        "completed_milestones": m_comp,
        "execution_partners": exec_partner_count,

        "pending_payouts": pay_stats["pending"] or 0,
        "completed_payouts": pay_stats["completed"] or 0,
        "available_balance": available_bal,

        "funding_percentage": funding_pct,
        "completion_percentage": completion_pct,

        "recent_donations": recent_donations,
        "recent_notifications": recent_notifications,
    }


def get_donor_dashboard(user, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Computes personalized analytical metrics for an individual donor.
    """
    params = params or {}
    if getattr(user, "role", None) != "donor":
        raise PermissionDenied("Only Donor users can access Donor analytics dashboard.")

    donations_qs = apply_analytics_filters(
        Donation.objects.filter(donor=user),
        params,
        campaign_field="campaign_id",
        ngo_field="campaign__created_by_id",
        search_fields=["campaign__title"],
    )

    don_stats = donations_qs.aggregate(
        total=Count("id"),
        success=Count("id", filter=Q(status="success")),
        pending=Count("id", filter=Q(status="pending")),
        refunded=Count("id", filter=Q(status="refunded")),
        total_amt=Coalesce(Sum("settled_amount", filter=Q(status="success")), Value(0), output_field=models.DecimalField(max_digits=14, decimal_places=2)),
        avg_amt=Coalesce(Avg("settled_amount", filter=Q(status="success")), Value(0), output_field=models.DecimalField(max_digits=14, decimal_places=2)),
        max_amt=Coalesce(Max("settled_amount", filter=Q(status="success")), Value(0), output_field=models.DecimalField(max_digits=14, decimal_places=2)),
    )

    campaigns_supported = donations_qs.filter(status="success").values("campaign").distinct().count()
    recent_donations = list(donations_qs.select_related("campaign", "donor").order_by("-created_at")[:5])
    recent_notifications = list(Notification.objects.filter(recipient=user).order_by("-created_at")[:5])

    return {
        "total_donations": don_stats["total"] or 0,
        "successful_donations": don_stats["success"] or 0,
        "pending_donations": don_stats["pending"] or 0,
        "refunded_donations": don_stats["refunded"] or 0,

        "total_amount_donated": Decimal(str(don_stats["total_amt"] or "0.00")),
        "average_donation": Decimal(str(don_stats["avg_amt"] or "0.00")),
        "largest_donation": Decimal(str(don_stats["max_amt"] or "0.00")),
        "campaigns_supported": campaigns_supported,

        "recent_donations": recent_donations,
        "recent_notifications": recent_notifications,
    }


def get_monthly_chart(chart_type: str, user, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    Computes uniform 12-month time-series aggregated data formatted directly for React chart component rendering.
    Uses ExtractMonth inside single database aggregations without any raw SQL.
    """
    params = params or {}
    user_role = getattr(user, "role", None)

    # Initialize 12-month zero-filled array
    chart_data = {m_int: {"month": m_label, "value": 0.0} for m_int, m_label in MONTH_MAP.items()}

    chart_clean = chart_type.lower().strip("/")
    if chart_clean == "donations":
        qs = Donation.objects.filter(status="success")
        if user_role == "ngo":
            qs = qs.filter(campaign__created_by=user)
        elif user_role == "donor":
            qs = qs.filter(donor=user)
        qs = apply_analytics_filters(qs, params, campaign_field="campaign_id")
        agg = qs.annotate(m=ExtractMonth("created_at")).values("m").annotate(val=Sum("settled_amount")).order_by("m")
        for row in agg:
            if row["m"] in chart_data:
                chart_data[row["m"]]["value"] = float(row["val"] or 0.0)

    elif chart_clean == "payouts":
        qs = Payout.objects.filter(is_deleted=False, status="completed")
        if user_role == "ngo":
            qs = qs.filter(campaign__created_by=user)
        elif user_role == "donor":
            return list(chart_data.values())  # Donors have no payout metrics
        qs = apply_analytics_filters(qs, params, campaign_field="campaign_id")
        agg = qs.annotate(m=ExtractMonth("created_at")).values("m").annotate(
            val=Sum(
                Case(
                    When(approved_amount__isnull=False, then=F("approved_amount")),
                    default=F("requested_amount"),
                    output_field=models.DecimalField(),
                )
            )
        ).order_by("m")
        for row in agg:
            if row["m"] in chart_data:
                chart_data[row["m"]]["value"] = float(row["val"] or 0.0)

    elif chart_clean == "campaigns":
        qs = Campaign.objects.all()
        if user_role == "ngo":
            qs = qs.filter(created_by=user)
        qs = apply_analytics_filters(qs, params)
        agg = qs.annotate(m=ExtractMonth("created_at")).values("m").annotate(val=Count("id")).order_by("m")
        for row in agg:
            if row["m"] in chart_data:
                chart_data[row["m"]]["value"] = float(row["val"] or 0.0)

    elif chart_clean == "users":
        if user_role != "admin":
            # Return platform donor engagement trends for non-admin viewers
            qs = Donation.objects.filter(status="success").values("donor").distinct()
        else:
            qs = User.objects.all()
        qs = apply_analytics_filters(qs, params, date_field="date_joined" if user_role == "admin" else "created_at")
        agg = qs.annotate(m=ExtractMonth("date_joined" if user_role == "admin" else "created_at")).values("m").annotate(val=Count("id")).order_by("m")
        for row in agg:
            if row["m"] in chart_data:
                chart_data[row["m"]]["value"] = float(row["val"] or 0.0)

    return list(chart_data.values())


def get_leaderboard(leaderboard_type: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    Computes ranked comparative leaderboard rankings using annotations, ExpressionWrappers, and aggregations.
    """
    params = params or {}
    l_type = leaderboard_type.lower().replace("-", "_").strip("/")
    results = []

    if l_type in ["top_campaigns", "highest_raised_campaigns"]:
        qs = apply_analytics_filters(
            Campaign.objects.filter(status__in=["live", "completed"]),
            params,
            search_fields=["title"],
        )
        top_qs = qs.order_by("-raised_amount")[:10]
        for idx, c in enumerate(top_qs, start=1):
            results.append({
                "rank": idx,
                "id": str(c.id),
                "name": c.title,
                "amount": Decimal(str(c.raised_amount or "0.00")),
                "count": 0,
            })

    elif l_type == "top_ngos":
        ngos = User.objects.filter(role="ngo", is_active=True)
        ngos = ngos.annotate(
            total_raised=Coalesce(
                Sum("campaigns__raised_amount", filter=Q(campaigns__status__in=["live", "completed"])),
                Value(0),
                output_field=models.DecimalField(max_digits=14, decimal_places=2),
            ),
            camp_cnt=Count("campaigns", filter=Q(campaigns__status__in=["live", "completed"])),
        ).order_by("-total_raised")[:10]
        for idx, u in enumerate(ngos, start=1):
            results.append({
                "rank": idx,
                "id": str(u.id),
                "name": u.full_name or u.email,
                "amount": Decimal(str(u.total_raised or "0.00")),
                "count": u.camp_cnt,
            })

    elif l_type == "top_donors":
        donors = User.objects.filter(role="donor", is_active=True)
        donors = donors.annotate(
            total_donated=Coalesce(
                Sum("donations__settled_amount", filter=Q(donations__status="success")),
                Value(0),
                output_field=models.DecimalField(max_digits=14, decimal_places=2),
            ),
            don_cnt=Count("donations", filter=Q(donations__status="success")),
        ).order_by("-total_donated")[:10]
        for idx, d in enumerate(donors, start=1):
            results.append({
                "rank": idx,
                "id": str(d.id),
                "name": d.full_name or d.email,
                "amount": Decimal(str(d.total_donated or "0.00")),
                "count": d.don_cnt,
            })

    elif l_type == "most_active_campaigns":
        qs = apply_analytics_filters(
            Campaign.objects.filter(status__in=["live", "completed"]),
            params,
            search_fields=["title"],
        )
        qs = qs.annotate(don_cnt=Count("donations", filter=Q(donations__status="success"))).order_by("-don_cnt")[:10]
        for idx, c in enumerate(qs, start=1):
            results.append({
                "rank": idx,
                "id": str(c.id),
                "name": c.title,
                "amount": Decimal(str(c.raised_amount or "0.00")),
                "count": c.don_cnt,
            })

    elif l_type == "largest_donations":
        qs = apply_analytics_filters(
            Donation.objects.filter(status="success").select_related("donor", "campaign"),
            params,
            campaign_field="campaign_id",
            ngo_field="campaign__created_by_id",
        )
        qs = qs.order_by("-settled_amount")[:10]
        for idx, d in enumerate(qs, start=1):
            donor_name = d.donor.email if (d.donor and not d.is_anonymous) else "Anonymous"
            results.append({
                "rank": idx,
                "id": str(d.id),
                "name": f"{donor_name} -> {d.campaign.title}",
                "amount": Decimal(str(d.settled_amount or "0.00")),
                "count": 1,
            })

    elif l_type == "largest_payouts":
        qs = apply_analytics_filters(
            Payout.objects.filter(is_deleted=False, status="completed").select_related("campaign", "ngo"),
            params,
            campaign_field="campaign_id",
            ngo_field="ngo_id",
        )
        # Sort by approved amount (or requested amount fallback)
        qs = qs.annotate(
            effective_amt=Coalesce("approved_amount", "requested_amount", output_field=models.DecimalField(max_digits=14, decimal_places=2))
        ).order_by("-effective_amt")[:10]
        for idx, p in enumerate(qs, start=1):
            results.append({
                "rank": idx,
                "id": str(p.id),
                "name": f"{p.ngo.email} ({p.campaign.title})",
                "amount": Decimal(str(p.approved_amount if p.approved_amount is not None else p.requested_amount)),
                "count": 1,
            })

    return results
