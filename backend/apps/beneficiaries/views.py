from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from .models import Beneficiary
from .permissions import BeneficiaryPermission
from .serializers import (
    BeneficiaryDetailSerializer,
    BeneficiaryListSerializer,
    BeneficiaryVerificationSerializer,
    BeneficiaryWriteSerializer,
)
from . import services
from grantloop.openapi import beneficiary_viewset_schema


@beneficiary_viewset_schema
class BeneficiaryViewSet(viewsets.ModelViewSet):
    """
    API viewset for managing beneficiary records.
    Delegates all queries and mutations to the service layer.
    """

    permission_classes = [BeneficiaryPermission]
    queryset = Beneficiary.objects.all()
    pagination_class = None  # Tests and API contract expect a direct list, not paginated dict
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["campaign", "verification_status"]
    search_fields = ["full_name", "email", "phone_number"]
    ordering_fields = ["created_at", "full_name"]
    ordering = ["-created_at"]


    def get_queryset(self):
        """
        Retrieves the base queryset scoped by requesting user role.
        """
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return Beneficiary.objects.none()
        return services.list_beneficiaries(user=self.request.user)

    def get_object(self):
        """
        Retrieves an object by primary key from the full active queryset (including
        records outside the user's filtered list, excluding soft-deleted records unless admin),
        and enforces object-level permissions so unauthorized access returns 403 instead of 404.
        """
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}

        if self.request.user and getattr(self.request.user, "role", None) == "admin":
            queryset = Beneficiary.objects.all_with_deleted()
        else:
            queryset = Beneficiary.objects.all()

        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj

    def get_serializer_class(self):
        if self.action == "list":
            return BeneficiaryListSerializer
        if self.action in ["create", "update", "partial_update"]:
            return BeneficiaryWriteSerializer
        if self.action in ["verify", "reject"]:
            return BeneficiaryVerificationSerializer
        return BeneficiaryDetailSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        beneficiary = services.create_beneficiary(
            user=request.user,
            **serializer.validated_data
        )

        response_serializer = BeneficiaryDetailSerializer(beneficiary, context={"request": request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        beneficiary = self.get_object()

        serializer = self.get_serializer(beneficiary, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        updated_beneficiary = services.update_beneficiary(
            beneficiary_id=str(beneficiary.id),
            user=request.user,
            **serializer.validated_data
        )

        response_serializer = BeneficiaryDetailSerializer(updated_beneficiary, context={"request": request})
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        beneficiary = self.get_object()
        services.delete_beneficiary(beneficiary_id=str(beneficiary.id), user=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="verify")
    def verify(self, request, pk=None):
        beneficiary = self.get_object()
        verified_beneficiary = services.verify_beneficiary(beneficiary_id=str(beneficiary.id), user=request.user)
        response_serializer = BeneficiaryDetailSerializer(verified_beneficiary, context={"request": request})
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        beneficiary = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        rejection_reason = serializer.validated_data.get("rejection_reason", "")
        rejected_beneficiary = services.reject_beneficiary(
            beneficiary_id=str(beneficiary.id),
            user=request.user,
            rejection_reason=rejection_reason,
        )

        response_serializer = BeneficiaryDetailSerializer(rejected_beneficiary, context={"request": request})
        return Response(response_serializer.data, status=status.HTTP_200_OK)
