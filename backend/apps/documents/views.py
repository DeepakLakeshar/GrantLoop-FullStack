from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied as DRFPermissionDenied
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from . import services
from .models import Document
from .permissions import IsAuthenticatedForWrite
from .serializers import DocumentReviewSerializer, DocumentSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    """
    Unlike Milestones/CampaignUpdates, Documents require authentication
    even to read — beneficiary-scoped documents (government ID, etc.)
    are personal data, not public evidence. get_queryset narrows further:
    a non-privileged user never sees beneficiary-scoped rows at all.
    """

    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticatedForWrite]
    parser_classes = [MultiPartParser, FormParser]
    http_method_names = ["get", "post", "delete", "head", "options"]  # no edit — re-upload instead

    def get_serializer_context(self):
        return {**super().get_serializer_context(), "request": self.request}

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        campaign_id = self.request.query_params.get("campaign")
        if campaign_id:
            qs = qs.filter(campaign_id=campaign_id)

        if user.role in ("admin", "institution"):
            return qs
        # A non-privileged user (donor, ngo, execution_partner) never
        # sees beneficiary-scoped documents unless they uploaded it
        # themselves — government ID and similar personal data isn't
        # public evidence just because the campaign is.
        from django.db.models import Q
        return qs.filter(Q(beneficiary__isnull=True) | Q(uploaded_by=user))

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)
        file = data.pop("file")
        document_type = data.pop("document_type")
        try:
            document = services.upload_document(
                actor=request.user, file=file, document_type=document_type, **data
            )
        except DjangoPermissionDenied as exc:
            raise DRFPermissionDenied(str(exc))
        except DjangoValidationError as exc:
            raise DRFValidationError(str(exc))
        return Response(self.get_serializer(document).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        document = self.get_object()
        try:
            services.delete_document(document=document, actor=request.user)
        except DjangoPermissionDenied as exc:
            raise DRFPermissionDenied(str(exc))
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def review(self, request, pk=None):
        document = self.get_object()
        serializer = DocumentReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            document = services.review_document(
                document=document, actor=request.user, new_status=serializer.validated_data["status"]
            )
        except DjangoPermissionDenied as exc:
            raise DRFPermissionDenied(str(exc))
        return Response(self.get_serializer(document).data)
