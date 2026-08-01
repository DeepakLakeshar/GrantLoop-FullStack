from django.urls import path
from . import views

urlpatterns = [
    path("donations/", views.DonationReportView.as_view(), name="report-donations"),
    path("donations/export/", views.DonationReportExportView.as_view(), name="report-donations-export"),

    path("campaigns/", views.CampaignReportView.as_view(), name="report-campaigns"),
    path("campaigns/export/", views.CampaignReportExportView.as_view(), name="report-campaigns-export"),

    path("ngos/", views.NGOReportView.as_view(), name="report-ngos"),
    path("ngos/export/", views.NGOReportExportView.as_view(), name="report-ngos-export"),

    path("beneficiaries/", views.BeneficiaryReportView.as_view(), name="report-beneficiaries"),
    path("beneficiaries/export/", views.BeneficiaryReportExportView.as_view(), name="report-beneficiaries-export"),

    path("payouts/", views.PayoutReportView.as_view(), name="report-payouts"),
    path("payouts/export/", views.PayoutReportExportView.as_view(), name="report-payouts-export"),

    path("financial/", views.FinancialReportView.as_view(), name="report-financial"),
    path("financial/export/", views.FinancialReportExportView.as_view(), name="report-financial-export"),

    path("audit-logs/", views.AuditLogReportView.as_view(), name="report-audit-logs"),
    path("audit-logs/export/", views.AuditLogReportExportView.as_view(), name="report-audit-logs-export"),
]
