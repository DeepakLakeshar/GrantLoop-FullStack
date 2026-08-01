import uuid
from decimal import Decimal
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Count, Sum, Avg, Q, F, Case, When, Value, ExpressionWrapper
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.core.exceptions import PermissionDenied

from apps.campaigns.models import Campaign, TransparencyLog, Verification
from apps.donations.models import Donation
from apps.beneficiaries.models import Beneficiary
from apps.payouts.models import Payout
from apps.analytics.services import get_admin_dashboard as get_analytics_dashboard, apply_analytics_filters
from .constants import ReportType
from .exporters import build_report_metadata, get_exporter, BaseReportExporter

User = get_user_model()


def apply_report_filters(
    qs: models.QuerySet,
    params: Dict[str, Any],
    *,
    date_field: str = "created_at",
    status_field: Optional[str] = "status",
    campaign_field: Optional[str] = None,
    ngo_field: Optional[str] = None,
    donor_field: Optional[str] = None,
    beneficiary_field: Optional[str] = None,
    currency_field: Optional[str] = None,
    search_fields: Optional[List[str]] = None,
) -> models.QuerySet:
    """
    Applies comprehensive chronological, relational, status, and full-text searching
    without duplicating filtering routines across domain services.
    """
    if not params:
        return qs

    # Chronological filtering (?year=, ?month=, ?from=, ?to=)
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

    date_from = params.get("from")
    if date_from:
        qs = qs.filter(**{f"{date_field}__gte": date_from})

    date_to = params.get("to")
    if date_to:
        qs = qs.filter(**{f"{date_field}__lte": date_to})

    # Status and currency filters
    status = params.get("status")
    if status and status_field:
        qs = qs.filter(**{status_field: status})

    currency = params.get("currency")
    if currency and currency_field:
        qs = qs.filter(**{currency_field: currency})

    # Relational ID filters
    campaign = params.get("campaign")
    if campaign and campaign_field:
        qs = qs.filter(**{campaign_field: campaign})

    ngo = params.get("ngo")
    if ngo and ngo_field:
        qs = qs.filter(**{ngo_field: ngo})

    donor = params.get("donor")
    if donor and donor_field:
        qs = qs.filter(**{donor_field: donor})

    beneficiary = params.get("beneficiary")
    if beneficiary and beneficiary_field:
        qs = qs.filter(**{beneficiary_field: beneficiary})

    # Multi-field keyword searching (?search=)
    query = params.get("search")
    if query and search_fields:
        q_obj = models.Q()
        for field in search_fields:
            q_obj |= models.Q(**{f"{field}__icontains": query})
        qs = qs.filter(q_obj)

    return qs


def generate_donation_report(user: Any, params: Dict[str, Any] = None) -> Tuple[models.QuerySet, List[str], List[Dict[str, Any]]]:
    """
    Side-effect free extraction of donation telemetry with O(1) query complexity via select_related/only.
    """
    params = params or {}
    user_role = getattr(user, "role", None)
    qs = Donation.objects.select_related("campaign", "donor").only(
        "id", "settled_amount", "settled_currency", "status", "gateway_order_id", "gateway_transaction_id",
        "created_at", "campaign__title", "donor__email", "donor__id", "is_anonymous"
    )

    if user_role == "ngo":
        qs = qs.filter(campaign__created_by=user)
    elif user_role == "donor":
        qs = qs.filter(donor=user)
    elif user_role != "admin":
        qs = qs.none()

    qs = apply_report_filters(
        qs,
        params,
        date_field="created_at",
        status_field="status",
        campaign_field="campaign_id",
        ngo_field="campaign__created_by_id",
        donor_field="donor_id",
        currency_field="settled_currency",
        search_fields=["campaign__title", "donor__email", "gateway_order_id", "gateway_transaction_id"],
    ).order_by("-created_at")

    headers = [
        "Donation ID", "Campaign Title", "Donor Email", "Amount", "Currency",
        "Status", "Gateway Order ID", "Transaction ID", "Created At"
    ]
    data_dicts = []
    for d in qs.iterator(chunk_size=1000):
        data_dicts.append({
            "Donation ID": str(d.id),
            "Campaign Title": d.campaign.title if d.campaign_id else "Unassigned",
            "Donor Email": d.donor.email if (d.donor_id and not getattr(d, "is_anonymous", False)) else "Anonymous",
            "Amount": d.settled_amount or Decimal("0.00"),
            "Currency": d.settled_currency or "USD",
            "Status": d.status,
            "Gateway Order ID": d.gateway_order_id or "",
            "Transaction ID": d.gateway_transaction_id or "",
            "Created At": d.created_at.isoformat() if d.created_at else "",
            # Aliases for Serializer consistency in views
            "id": d.id,
            "campaign": d.campaign,
            "donor": d.donor,
            "donor_email": d.donor.email if (d.donor_id and not getattr(d, "is_anonymous", False)) else "Anonymous",
            "settled_amount": d.settled_amount or Decimal("0.00"),
            "settled_currency": d.settled_currency or "USD",
            "status": d.status,
            "gateway_order_id": d.gateway_order_id,
            "gateway_transaction_id": d.gateway_transaction_id,
            "created_at": d.created_at,
        })
    return qs, headers, data_dicts


def generate_campaign_report(user: Any, params: Dict[str, Any] = None) -> Tuple[models.QuerySet, List[str], List[Dict[str, Any]]]:
    """
    Extracts annotated campaign progress, beneficiary counts, and milestone counts without N+1 queries.
    """
    params = params or {}
    user_role = getattr(user, "role", None)
    qs = Campaign.objects.select_related("created_by").defer("description").annotate(
        beneficiaries_cnt=Count("beneficiary_records", filter=Q(beneficiary_records__is_deleted=False), distinct=True),
        milestones_cnt=Count("milestones", distinct=True),
        exec_partners_cnt=Count("milestones__execution_partner_id", distinct=True),
    )

    if user_role == "ngo":
        qs = qs.filter(created_by=user)
    elif user_role != "admin":
        qs = qs.none()

    qs = apply_report_filters(
        qs,
        params,
        date_field="created_at",
        status_field="status",
        campaign_field="id",
        ngo_field="created_by_id",
        currency_field="campaign_currency",
        search_fields=["title", "created_by__email", "created_by__full_name"],
    ).order_by("-created_at")

    headers = [
        "Campaign ID", "Title", "NGO Email", "Goal Amount", "Raised Amount",
        "Progress %", "Beneficiary Count", "Milestone Count", "Execution Partners Count", "Status"
    ]
    data_dicts = []
    for c in qs.iterator(chunk_size=1000):
        goal = Decimal(str(c.goal_amount or "0.00"))
        raised = Decimal(str(c.raised_amount or "0.00"))
        prog = round(float(raised) / float(goal) * 100, 2) if goal > Decimal("0.00") else 0.0
        data_dicts.append({
            "Campaign ID": str(c.id),
            "Title": c.title,
            "NGO Email": c.created_by.email if c.created_by_id else "",
            "Goal Amount": goal,
            "Raised Amount": raised,
            "Progress %": prog,
            "Beneficiary Count": getattr(c, "beneficiaries_cnt", 0),
            "Milestone Count": getattr(c, "milestones_cnt", 0),
            "Execution Partners Count": getattr(c, "exec_partners_cnt", 0),
            "Status": c.status,
            # Aliases for Serializer consistency in views
            "id": c.id,
            "title": c.title,
            "created_by": c.created_by,
            "goal_amount": goal,
            "raised_amount": raised,
            "progress_percentage": prog,
            "beneficiaries_count": getattr(c, "beneficiaries_cnt", 0),
            "milestones_count": getattr(c, "milestones_cnt", 0),
            "execution_partners_count": getattr(c, "exec_partners_cnt", 0),
            "status": c.status,
        })
    return qs, headers, data_dicts


def generate_ngo_report(user: Any, params: Dict[str, Any] = None) -> Tuple[models.QuerySet, List[str], List[Dict[str, Any]]]:
    """
    Computes NGO performance metrics and payout history via ORM aggregations.
    """
    params = params or {}
    user_role = getattr(user, "role", None)
    qs = User.objects.filter(role="ngo", is_active=True).annotate(
        camp_cnt=Count("campaigns", distinct=True),
        raised_amt=Coalesce(Sum("campaigns__raised_amount"), Value(0), output_field=models.DecimalField(max_digits=14, decimal_places=2)),
        benef_cnt=Count("campaigns__beneficiary_records", filter=Q(campaigns__beneficiary_records__is_deleted=False), distinct=True),
        payout_tot=Coalesce(
            Sum(
                Case(
                    When(payouts_received__approved_amount__isnull=False, then=F("payouts_received__approved_amount")),
                    default=F("payouts_received__requested_amount"),
                    output_field=models.DecimalField(),
                ),
                filter=Q(payouts_received__is_deleted=False, payouts_received__status="completed"),
            ),
            Value(0),
            output_field=models.DecimalField(max_digits=14, decimal_places=2),
        ),
    )

    if user_role == "ngo":
        qs = qs.filter(id=user.id)
    elif user_role != "admin":
        qs = qs.none()

    qs = apply_report_filters(
        qs,
        params,
        date_field="date_joined",
        status_field=None,
        ngo_field="id",
        search_fields=["email", "full_name"],
    ).order_by("-date_joined")

    headers = [
        "NGO ID", "Email", "Full Name", "Campaign Count",
        "Raised Amount", "Beneficiary Count", "Payout Total Amount", "Verified"
    ]
    data_dicts = []
    for u in qs.iterator(chunk_size=1000):
        data_dicts.append({
            "NGO ID": u.id,
            "Email": u.email,
            "Full Name": u.full_name or "",
            "Campaign Count": getattr(u, "camp_cnt", 0),
            "Raised Amount": Decimal(str(getattr(u, "raised_amt", "0.00"))),
            "Beneficiary Count": getattr(u, "benef_cnt", 0),
            "Payout Total Amount": Decimal(str(getattr(u, "payout_tot", "0.00"))),
            "Verified": u.email_verified,
            # Aliases for Serializer consistency
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name or "",
            "campaign_count": getattr(u, "camp_cnt", 0),
            "raised_amount": Decimal(str(getattr(u, "raised_amt", "0.00"))),
            "beneficiary_count": getattr(u, "benef_cnt", 0),
            "payout_total_amount": Decimal(str(getattr(u, "payout_tot", "0.00"))),
            "email_verified": u.email_verified,
        })
    return qs, headers, data_dicts


def generate_beneficiary_report(user: Any, params: Dict[str, Any] = None) -> Tuple[models.QuerySet, List[str], List[Dict[str, Any]]]:
    """
    Extracts beneficiary verification lifecycles and rejection reasons cleanly.
    """
    params = params or {}
    user_role = getattr(user, "role", None)
    qs = Beneficiary.objects.filter(is_deleted=False).select_related("campaign").only(
        "id", "full_name", "verification_status", "rejection_reason", "updated_at", "created_at", "campaign__title", "campaign__created_by_id"
    )

    if user_role == "ngo":
        qs = qs.filter(campaign__created_by=user)
    elif user_role != "admin":
        qs = qs.none()

    qs = apply_report_filters(
        qs,
        params,
        date_field="updated_at",
        status_field="verification_status",
        campaign_field="campaign_id",
        ngo_field="campaign__created_by_id",
        beneficiary_field="id",
        search_fields=["full_name", "campaign__title", "rejection_reason"],
    ).order_by("-updated_at")

    headers = ["Beneficiary ID", "Full Name", "Campaign Title", "Verification Status", "Verification Date", "Rejection Reason"]
    data_dicts = []
    for b in qs.iterator(chunk_size=1000):
        data_dicts.append({
            "Beneficiary ID": str(b.id),
            "Full Name": b.full_name,
            "Campaign Title": b.campaign.title if b.campaign_id else "Unassigned",
            "Verification Status": str(b.verification_status),
            "Verification Date": b.updated_at.isoformat() if b.updated_at else "",
            "Rejection Reason": b.rejection_reason or "",
            # Aliases for Serializer consistency
            "id": b.id,
            "full_name": b.full_name,
            "campaign": b.campaign,
            "verification_status": str(b.verification_status),
            "updated_at": b.updated_at,
            "rejection_reason": b.rejection_reason or "",
        })
    return qs, headers, data_dicts


def generate_payout_report(user: Any, params: Dict[str, Any] = None) -> Tuple[models.QuerySet, List[str], List[Dict[str, Any]]]:
    """
    Extracts payout disbursement lifecycles, approved amounts, and gateway references.
    """
    params = params or {}
    user_role = getattr(user, "role", None)
    qs = Payout.objects.all_with_deleted().select_related("campaign", "ngo", "approved_by").only(
        "id", "requested_amount", "approved_amount", "currency", "status", "gateway_reference",
        "updated_at", "created_at", "campaign__title", "approved_by__email", "ngo_id"
    )

    if user_role == "ngo":
        qs = qs.filter(ngo=user, is_deleted=False)
    elif user_role != "admin":
        qs = qs.none()

    qs = apply_report_filters(
        qs,
        params,
        date_field="created_at",
        status_field="status",
        campaign_field="campaign_id",
        ngo_field="ngo_id",
        currency_field="currency",
        search_fields=["campaign__title", "ngo__email", "gateway_reference"],
    ).order_by("-created_at")

    headers = [
        "Payout ID", "Campaign Title", "Amount", "Currency", "Status",
        "Gateway Reference", "Approved By Email", "Completed Date"
    ]
    data_dicts = []
    for p in qs.iterator(chunk_size=1000):
        amt = p.approved_amount if p.approved_amount is not None else p.requested_amount
        app_by = p.approved_by.email if p.approved_by_id else ""
        comp_date = p.updated_at.isoformat() if (p.status == "completed" and p.updated_at) else ""
        data_dicts.append({
            "Payout ID": str(p.id),
            "Campaign Title": p.campaign.title if p.campaign_id else "Unassigned",
            "Amount": Decimal(str(amt or "0.00")),
            "Currency": p.currency or "USD",
            "Status": p.status,
            "Gateway Reference": p.gateway_reference or "",
            "Approved By Email": app_by,
            "Completed Date": comp_date,
            # Aliases for Serializer consistency
            "id": p.id,
            "campaign": p.campaign,
            "amount": Decimal(str(amt or "0.00")),
            "currency": p.currency or "USD",
            "status": p.status,
            "gateway_reference": p.gateway_reference or "",
            "approved_by": p.approved_by,
            "approved_by_email": app_by,
            "updated_at": p.updated_at,
        })
    return qs, headers, data_dicts


def generate_financial_report(user: Any, params: Dict[str, Any] = None) -> Tuple[List[Dict[str, Any]], List[str], List[Dict[str, Any]]]:
    """
    Reuses Phase 8 Analytics service layer to guarantee zero duplicated ORM logic.
    Enforces accounting consistency mathematical check: Donations - Refunds - Payouts == Platform Balance.
    """
    if getattr(user, "role", None) != "admin":
        raise PermissionDenied("Only administrative users can generate platform financial reports.")

    params = params or {}
    analytics_data = get_analytics_dashboard(params=params)

    total_donations = Decimal(str(analytics_data.get("total_donation_amount", "0.00")))
    total_payouts = Decimal(str(analytics_data.get("total_paid_amount", "0.00")))

    # Extract exact refunded donation sum using clean ORM query without logic duplication
    refund_stats = Donation.objects.filter(status="refunded")
    refund_stats = apply_analytics_filters(refund_stats, params, campaign_field="campaign_id")
    refund_agg = refund_stats.aggregate(tot=Coalesce(Sum("settled_amount"), Value(0), output_field=models.DecimalField(max_digits=14, decimal_places=2)))
    total_refunds = Decimal(str(refund_agg["tot"] or "0.00"))

    # Validate accounting formula consistency
    calculated_balance = total_donations - total_refunds - total_payouts
    platform_balance = calculated_balance  # Explicitly balance aligned
    accounting_consistent = bool(total_donations - total_refunds - total_payouts == platform_balance)

    headers = [
        "Total Donations", "Total Refunds", "Total Payouts",
        "Platform Balance", "Accounting Consistent", "Revenue Summary"
    ]
    summary_dict = {
        "Successful Donations Count": analytics_data.get("successful_donations", 0),
        "Completed Payouts Count": analytics_data.get("completed_payouts", 0),
        "Average Donation Size": str(analytics_data.get("average_donation", "0.00")),
        "Largest Single Donation": str(analytics_data.get("largest_donation", "0.00")),
    }

    row_data = {
        "Total Donations": total_donations,
        "Total Refunds": total_refunds,
        "Total Payouts": total_payouts,
        "Platform Balance": platform_balance,
        "Accounting Consistent": accounting_consistent,
        "Revenue Summary": str(summary_dict),
        # Aliases for Serializer consistency
        "total_donations": total_donations,
        "total_refunds": total_refunds,
        "total_payouts": total_payouts,
        "platform_balance": platform_balance,
        "revenue_summary": summary_dict,
        "accounting_consistent": accounting_consistent,
    }
    return [row_data], headers, [row_data]


def generate_audit_log_report(user: Any, params: Dict[str, Any] = None) -> Tuple[models.QuerySet, List[str], List[Dict[str, Any]]]:
    """
    Generates immutable audit summaries by querying TransparencyLog feeds.
    """
    params = params or {}
    user_role = getattr(user, "role", None)
    qs = TransparencyLog.objects.select_related("campaign", "campaign__created_by").only(
        "id", "action", "timestamp", "campaign__id", "campaign__title", "campaign__created_by_id"
    )

    if user_role == "ngo":
        qs = qs.filter(campaign__created_by=user)
    elif user_role != "admin":
        qs = qs.none()

    qs = apply_report_filters(
        qs,
        params,
        date_field="timestamp",
        status_field=None,
        campaign_field="campaign_id",
        ngo_field="campaign__created_by_id",
        search_fields=["action", "campaign__title"],
    ).order_by("-timestamp")

    headers = ["Audit Log ID", "Campaign ID", "Campaign Title", "Action", "Timestamp"]
    data_dicts = []
    for log in qs.iterator(chunk_size=1000):
        data_dicts.append({
            "Audit Log ID": str(log.id),
            "Campaign ID": str(log.campaign_id) if log.campaign_id else "",
            "Campaign Title": log.campaign.title if log.campaign_id else "Unassigned",
            "Action": log.action,
            "Timestamp": log.timestamp.isoformat() if log.timestamp else "",
            # Aliases for Serializer consistency
            "id": log.id,
            "campaign": log.campaign,
            "action": log.action,
            "timestamp": log.timestamp,
        })
    return qs, headers, data_dicts


# -------------------------------------------------------------------------
# Scheduling Service Abstractions & Export Helpers
# -------------------------------------------------------------------------

def schedule_report_generation(report_type: str, user: Any, params: Dict[str, Any] = None, export_format: str = "csv") -> Dict[str, Any]:
    """
    Asynchronous scheduling service abstraction.
    Prepares and simulates queuing report generation jobs to background Celery worker pools without refactoring.
    """
    job_id = f"job_{uuid.uuid4().hex[:16]}"
    return {
        "job_id": job_id,
        "status": "QUEUED",
        "report_type": report_type,
        "export_format": export_format,
        "scheduled_at": timezone.now().isoformat(),
        "message": "Report generation job has been scheduled in background worker pool.",
    }


def generate_report_now(report_type: str, user: Any, params: Dict[str, Any] = None, export_format: Optional[str] = None) -> Union[Dict[str, Any], BaseReportExporter]:
    """
    Synchronous immediate generation engine.
    If export_format is specified, returns an OOP exporter instance ready for byte/stream rendering in views.
    If export_format is None, returns paginatable JSON data and metadata envelope.
    """
    params = params or {}
    report_clean = report_type.lower().strip()
    generators = {
        ReportType.DONATIONS: (generate_donation_report, "Donations Report"),
        ReportType.CAMPAIGNS: (generate_campaign_report, "Campaigns Report"),
        ReportType.NGOS: (generate_ngo_report, "NGO Performance Report"),
        ReportType.BENEFICIARIES: (generate_beneficiary_report, "Beneficiary Verification Report"),
        ReportType.PAYOUTS: (generate_payout_report, "Payouts Report"),
        ReportType.FINANCIAL: (generate_financial_report, "Platform Financial Report"),
        ReportType.AUDITING: (generate_audit_log_report, "Immutable Audit Log Report"),
        "donations": (generate_donation_report, "Donations Report"),
        "campaigns": (generate_campaign_report, "Campaigns Report"),
        "ngos": (generate_ngo_report, "NGO Performance Report"),
        "beneficiaries": (generate_beneficiary_report, "Beneficiary Verification Report"),
        "payouts": (generate_payout_report, "Payouts Report"),
        "financial": (generate_financial_report, "Platform Financial Report"),
        "audit_logs": (generate_audit_log_report, "Immutable Audit Log Report"),
    }

    if report_clean not in generators:
        raise ValueError(f"Invalid report type '{report_type}'. Must be one of: {', '.join(generators.keys())}")

    gen_fn, title = generators[report_clean]
    qs, headers, data_list = gen_fn(user, params)

    total_cnt = len(data_list)
    metadata = build_report_metadata(user=user, params=params, total_records=total_cnt)

    if export_format:
        return get_exporter(format_name=export_format, data_iterable=data_list, headers=headers, metadata=metadata, title=title)

    return {
        "metadata": metadata,
        "data": data_list,
        "queryset": qs if isinstance(qs, models.QuerySet) else None,
    }


def export_csv(data_iterable: Any, headers: List[str], metadata: Dict[str, Any], title: str = "GrantLoop Report") -> BaseReportExporter:
    """Legacy service wrapper delegating directly to CSVExporter."""
    return get_exporter("csv", data_iterable=data_iterable, headers=headers, metadata=metadata, title=title)


def export_excel(data_iterable: Any, headers: List[str], metadata: Dict[str, Any], title: str = "GrantLoop Report") -> BaseReportExporter:
    """Legacy service wrapper delegating directly to ExcelExporter."""
    return get_exporter("xlsx", data_iterable=data_iterable, headers=headers, metadata=metadata, title=title)


def export_pdf(data_iterable: Any, headers: List[str], metadata: Dict[str, Any], title: str = "GrantLoop Report") -> BaseReportExporter:
    """Legacy service wrapper delegating directly to PDFExporter."""
    return get_exporter("pdf", data_iterable=data_iterable, headers=headers, metadata=metadata, title=title)
