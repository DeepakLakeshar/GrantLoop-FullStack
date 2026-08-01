from django.db import models

REPORT_VERSION = "v1.0"

VALID_EXPORT_FORMATS = ("csv", "xlsx", "pdf")


class ReportType(models.TextChoices):
    DONATIONS = "donations", "Donation Report"
    CAMPAIGNS = "campaigns", "Campaign Report"
    NGOS = "ngos", "NGO Report"
    BENEFICIARIES = "beneficiaries", "Beneficiary Report"
    PAYOUTS = "payouts", "Payout Report"
    FINANCIAL = "financial", "Financial Report"
    AUDITING = "audit_logs", "Audit Log Report"


# Registry mapping format strings to class names in exporters.py
# (String identifiers prevent cyclic dependency resolution during package load)
EXPORTER_REGISTRY = {
    "csv": "CSVExporter",
    "xlsx": "ExcelExporter",
    "pdf": "PDFExporter",
    "zip": "ZIPExporter",
}
