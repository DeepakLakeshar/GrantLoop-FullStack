from rest_framework.throttling import UserRateThrottle


class ReportExportThrottle(UserRateThrottle):
    """
    Rate limiter applied to CPU/memory intensive report document generation
    endpoints to prevent resource exhaustion and programmatic abuse.
    """
    scope = "report_export"
    rate = "100/minute"

    def get_rate(self):
        return self.rate
