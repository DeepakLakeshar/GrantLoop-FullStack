from django.http import HttpResponse, StreamingHttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from grantloop.openapi import report_export_schema, report_json_schema

from . import services, serializers, permissions, throttles
from .constants import VALID_EXPORT_FORMATS, ReportType


class ReportPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 500


class BaseReportJSONView(APIView):
    """
    Thin base controller serving paginated JSON report feeds and metadata envelopes.
    """
    report_type: str = None
    serializer_class = None

    @report_json_schema
    def get(self, request):
        params = request.query_params.dict()
        if params.get("schedule") == "true":
            ticket = services.schedule_report_generation(self.report_type, request.user, params, export_format="json")
            return Response(ticket, status=status.HTTP_202_ACCEPTED)

        res = services.generate_report_now(self.report_type, request.user, params, export_format=None)
        data_list = res["data"]
        metadata = res["metadata"]

        paginator = ReportPagination()
        page = paginator.paginate_queryset(data_list, request, view=self)

        if page is not None and self.serializer_class:
            serializer = self.serializer_class(page, many=True)
            return paginator.get_paginated_response({
                "metadata": metadata,
                "records": serializer.data
            })
        elif self.serializer_class:
            serializer = self.serializer_class(data_list, many=True)
            return Response({"metadata": metadata, "records": serializer.data}, status=status.HTTP_200_OK)

        return Response({"metadata": metadata, "records": data_list}, status=status.HTTP_200_OK)


class BaseReportExportView(APIView):
    """
    Thin base controller executing unpaginated document streaming (CSV, XLSX, PDF).
    Exporters return raw content only; HttpResponse objects are forged exclusively in this controller layer.
    """
    report_type: str = None
    throttle_classes = [throttles.ReportExportThrottle]

    def perform_content_negotiation(self, request, force=False):
        # Prevent DRF content negotiation from interpreting ?format=csv/xlsx/pdf as an unregistered renderer format and throwing 404
        renderers = self.get_renderers()
        return (renderers[0], renderers[0].media_type)

    @report_export_schema
    def get(self, request):
        params = request.query_params.dict()
        fmt = params.get("format", "").lower().strip()

        if fmt not in VALID_EXPORT_FORMATS:
            return Response(
                {"error": f"Invalid export format '{fmt}'. Valid formats are: {', '.join(VALID_EXPORT_FORMATS)}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if params.get("schedule") == "true":
            ticket = services.schedule_report_generation(self.report_type, request.user, params, export_format=fmt)
            return Response(ticket, status=status.HTTP_202_ACCEPTED)

        exporter = services.generate_report_now(self.report_type, request.user, params, export_format=fmt)

        timestamp_str = timezone.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"grantloop_{self.report_type}_{timestamp_str}.{fmt}"

        if fmt == "csv":
            content_generator = exporter.generate_content()
            response = StreamingHttpResponse(content_generator, content_type="text/csv")
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response

        elif fmt == "xlsx":
            content_bytes = exporter.generate_content()
            response = HttpResponse(
                content_bytes,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response

        elif fmt == "pdf":
            content_bytes = exporter.generate_content()
            response = HttpResponse(content_bytes, content_type="application/pdf")
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response

        return Response({"error": "Failed to craft export document response."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# -------------------------------------------------------------------------
# Concrete JSON Report Views
# -------------------------------------------------------------------------

class DonationReportView(BaseReportJSONView):
    permission_classes = [permissions.CanAccessDonationReports]
    report_type = ReportType.DONATIONS
    serializer_class = serializers.DonationReportSerializer


class CampaignReportView(BaseReportJSONView):
    permission_classes = [permissions.CanAccessOperationalReports]
    report_type = ReportType.CAMPAIGNS
    serializer_class = serializers.CampaignReportSerializer


class NGOReportView(BaseReportJSONView):
    permission_classes = [permissions.CanAccessNGOReports]
    report_type = ReportType.NGOS
    serializer_class = serializers.NGOReportSerializer


class BeneficiaryReportView(BaseReportJSONView):
    permission_classes = [permissions.CanAccessOperationalReports]
    report_type = ReportType.BENEFICIARIES
    serializer_class = serializers.BeneficiaryReportSerializer


class PayoutReportView(BaseReportJSONView):
    permission_classes = [permissions.CanAccessOperationalReports]
    report_type = ReportType.PAYOUTS
    serializer_class = serializers.PayoutReportSerializer


class FinancialReportView(BaseReportJSONView):
    permission_classes = [permissions.CanAccessFinancialReports]
    report_type = ReportType.FINANCIAL
    serializer_class = serializers.FinancialReportSerializer


class AuditLogReportView(BaseReportJSONView):
    permission_classes = [permissions.CanAccessOperationalReports]
    report_type = ReportType.AUDITING
    serializer_class = serializers.AuditLogReportSerializer


# -------------------------------------------------------------------------
# Concrete Unpaginated Export Views
# -------------------------------------------------------------------------

class DonationReportExportView(BaseReportExportView):
    permission_classes = [permissions.CanAccessDonationReports]
    report_type = ReportType.DONATIONS


class CampaignReportExportView(BaseReportExportView):
    permission_classes = [permissions.CanAccessOperationalReports]
    report_type = ReportType.CAMPAIGNS


class NGOReportExportView(BaseReportExportView):
    permission_classes = [permissions.CanAccessNGOReports]
    report_type = ReportType.NGOS


class BeneficiaryReportExportView(BaseReportExportView):
    permission_classes = [permissions.CanAccessOperationalReports]
    report_type = ReportType.BENEFICIARIES


class PayoutReportExportView(BaseReportExportView):
    permission_classes = [permissions.CanAccessOperationalReports]
    report_type = ReportType.PAYOUTS


class FinancialReportExportView(BaseReportExportView):
    permission_classes = [permissions.CanAccessFinancialReports]
    report_type = ReportType.FINANCIAL


class AuditLogReportExportView(BaseReportExportView):
    permission_classes = [permissions.CanAccessOperationalReports]
    report_type = ReportType.AUDITING
