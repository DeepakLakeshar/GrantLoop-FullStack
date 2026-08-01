from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied as DRFPermissionDenied, ValidationError

from .models import ExecutionPartner
from .permissions import ExecutionPartnerPermission
from .serializers import (
    ExecutionPartnerDetailSerializer,
    ExecutionPartnerListSerializer,
    ExecutionPartnerWriteSerializer,
)
from . import services


class ExecutionPartnerViewSet(viewsets.ModelViewSet):
    """
    Execution Partners management endpoint.
    Allows listing, retrieval, admin-only creation, and owner/admin updates.
    Integrates directly with the service layer to execute CRUD state mutations.
    """
    queryset = ExecutionPartner.objects.select_related("user").all()
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_permissions(self):
        return [ExecutionPartnerPermission()]

    def get_queryset(self):
        return super().get_queryset()

    def get_serializer_class(self):
        if self.action == "list":
            return ExecutionPartnerListSerializer
        if self.action == "retrieve":
            return ExecutionPartnerDetailSerializer
        return ExecutionPartnerWriteSerializer

    def perform_create(self, serializer):
        user = serializer.validated_data.get("user")
        organization = serializer.validated_data.get("organization", "")
        try:
            partner = services.create_partner(
                actor=self.request.user,
                user=user,
                organization=organization
            )
            serializer.instance = partner
        except DjangoPermissionDenied as exc:
            raise DRFPermissionDenied(str(exc))
        except ValueError as exc:
            raise ValidationError(str(exc))

    def perform_update(self, serializer):
        partner = self.get_object()
        fields = serializer.validated_data
        try:
            updated_partner = services.update_partner(
                actor=self.request.user,
                partner=partner,
                **fields
            )
            serializer.instance = updated_partner
        except DjangoPermissionDenied as exc:
            raise DRFPermissionDenied(str(exc))
        except ValueError as exc:
            raise ValidationError(str(exc))








