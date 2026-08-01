from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.exceptions import PermissionDenied as DRFPermissionDenied, ValidationError
from rest_framework.response import Response

from .models import Payout
from .permissions import PayoutPermission
from .serializers import (
    PayoutListSerializer,
    PayoutDetailSerializer,
    PayoutCreateSerializer,
    PayoutApproveSerializer,
    PayoutRejectSerializer,
    PayoutProcessSerializer,
    PayoutCompleteSerializer,
    PayoutFailSerializer,
)
from . import services
from grantloop.openapi import payout_viewset_schema


@payout_viewset_schema
class PayoutViewSet(viewsets.ModelViewSet):
    """
    Thin ViewSet managing Payout lifecycle operations.
    Delegates entirely to services.py for business logic and state validation.
    Enforces 403 Forbidden responses for unauthorized access attempts against existing rows.
    """

    permission_classes = [PayoutPermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "campaign", "currency"]
    search_fields = [
        "campaign__title",
        "ngo__email",
        "gateway_reference",
        "transfer_reference",
        "request_notes",
        "admin_notes",
    ]
    ordering_fields = ["created_at", "requested_amount", "approved_at"]
    ordering = ["-created_at"]
    pagination_class = None  # Consistent with project conventions for direct-array list responses

    def get_queryset(self):
        """
        Retrieves role-scoped base queryset from service layer.
        """
        return services.list_payouts(user=self.request.user)

    def get_object(self):
        """
        Retrieves item from full active dataset (or all with deleted if admin)
        and explicitly evaluates object permissions to trigger HTTP 403 instead of 404
        when accessing existing rows out of standard list scope.
        """
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}

        if self.request.user and getattr(self.request.user, "role", None) == "admin":
            queryset = Payout.objects.all_with_deleted()
        else:
            queryset = Payout.objects.all()

        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj

    def get_serializer_class(self):
        if self.action == "list":
            return PayoutListSerializer
        if self.action == "create":
            return PayoutCreateSerializer
        if self.action == "approve":
            return PayoutApproveSerializer
        if self.action == "reject":
            return PayoutRejectSerializer
        if self.action == "process":
            return PayoutProcessSerializer
        if self.action == "complete":
            return PayoutCompleteSerializer
        if self.action == "fail":
            return PayoutFailSerializer
        return PayoutDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = PayoutCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            payout = services.create_payout_request(
                campaign=serializer.validated_data["campaign"],
                user=request.user,
                requested_amount=serializer.validated_data["requested_amount"],
                currency=serializer.validated_data.get("currency", "INR"),
                request_notes=serializer.validated_data.get("request_notes", ""),
            )
        except DjangoPermissionDenied as exc:
            raise DRFPermissionDenied(str(exc))
        except ValueError as exc:
            raise ValidationError(str(exc))

        return Response(PayoutDetailSerializer(payout).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        payout = self.get_object()
        try:
            services.cancel_payout(payout_id=payout.id, user=request.user)
        except DjangoPermissionDenied as exc:
            raise DRFPermissionDenied(str(exc))
        except ValueError as exc:
            raise ValidationError(str(exc))

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        payout = self.get_object()
        serializer = PayoutApproveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            updated_payout = services.approve_payout(
                payout_id=payout.id,
                admin_user=request.user,
                approved_amount=serializer.validated_data.get("approved_amount"),
                admin_notes=serializer.validated_data.get("admin_notes", ""),
            )
        except DjangoPermissionDenied as exc:
            raise DRFPermissionDenied(str(exc))
        except ValueError as exc:
            raise ValidationError(str(exc))

        return Response(PayoutDetailSerializer(updated_payout).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        payout = self.get_object()
        serializer = PayoutRejectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            updated_payout = services.reject_payout(
                payout_id=payout.id,
                admin_user=request.user,
                rejection_reason=serializer.validated_data.get("rejection_reason", ""),
                admin_notes=serializer.validated_data.get("admin_notes", ""),
            )
        except DjangoPermissionDenied as exc:
            raise DRFPermissionDenied(str(exc))
        except ValueError as exc:
            raise ValidationError(str(exc))

        return Response(PayoutDetailSerializer(updated_payout).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="process", url_name="process")
    def process(self, request, pk=None):
        payout = self.get_object()
        serializer = PayoutProcessSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            updated_payout = services.mark_processing(
                payout_id=payout.id,
                admin_user=request.user,
                gateway_type=serializer.validated_data.get("gateway_type", "mock"),
                account_reference=serializer.validated_data.get("account_reference", "default_acct"),
            )
        except DjangoPermissionDenied as exc:
            raise DRFPermissionDenied(str(exc))
        except ValueError as exc:
            raise ValidationError(str(exc))

        return Response(PayoutDetailSerializer(updated_payout).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="complete")
    def complete(self, request, pk=None):
        payout = self.get_object()
        serializer = PayoutCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            updated_payout = services.mark_completed(
                payout_id=payout.id,
                admin_user=request.user,
                transfer_reference=serializer.validated_data.get("transfer_reference", None),
            )
        except DjangoPermissionDenied as exc:
            raise DRFPermissionDenied(str(exc))
        except ValueError as exc:
            raise ValidationError(str(exc))

        return Response(PayoutDetailSerializer(updated_payout).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="fail")
    def fail(self, request, pk=None):
        payout = self.get_object()
        serializer = PayoutFailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            updated_payout = services.mark_failed(
                payout_id=payout.id,
                admin_user=request.user,
                failure_reason=serializer.validated_data.get("failure_reason", "Transfer failed at payment gateway."),
            )
        except DjangoPermissionDenied as exc:
            raise DRFPermissionDenied(str(exc))
        except ValueError as exc:
            raise ValidationError(str(exc))

        return Response(PayoutDetailSerializer(updated_payout).data, status=status.HTTP_200_OK)
