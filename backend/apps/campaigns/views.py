from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from common.permissions import IsInstitutionOrAdmin, IsNGO, IsOwnerNGOOrAdmin
from . import services
from .models import Beneficiary, Campaign, Category, TransparencyLog, Verification
from .serializers import (
    BeneficiarySerializer,
    CampaignDetailSerializer,
    CampaignListSerializer,
    CampaignWriteSerializer,
    CategorySerializer,
    TransparencyLogSerializer,
    VerificationSerializer,
)

PUBLIC_STATUSES = {"live", "completed"}


class CategoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Category listing — read-only, public. No write endpoint in Phase
    2A (categories are seeded via fixtures/admin, not user-created)."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.select_related("category", "created_by")
    http_method_names = ["get", "post", "patch", "head", "options"]  # no PUT, no direct DELETE

    def get_serializer_class(self):
        if self.action == "list":
            return CampaignListSerializer
        if self.action in ("create", "partial_update"):
            return CampaignWriteSerializer
        return CampaignDetailSerializer

    def get_permissions(self):
        if self.action in ("create",):
            return [IsAuthenticated(), IsNGO()]
        if self.action in ("partial_update", "submit", "archive"):
            return [IsAuthenticated(), IsOwnerNGOOrAdmin()]
        return [AllowAny()]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        params = self.request.query_params

        # Visibility: public sees only live/completed. An authenticated
        # NGO additionally sees its own campaigns regardless of status —
        # unconditionally, not just when ?mine=true, so that an object
        # lookup (submit/archive/partial_update/retrieve) on your own
        # draft campaign reaches the actual permission check instead of
        # 404ing before it gets there. ?mine=true is purely a list-view
        # narrowing filter on top of that. Institution/admin see
        # everything (needed for verification queues).
        if user.is_authenticated and user.role in ("admin", "institution"):
            pass
        elif user.is_authenticated and user.role == "ngo":
            qs = qs.filter(Q(created_by=user) | Q(status__in=PUBLIC_STATUSES))
            if params.get("mine") == "true":
                qs = qs.filter(created_by=user)
        else:
            qs = qs.filter(status__in=PUBLIC_STATUSES)

        if search := params.get("search"):
            qs = qs.filter(title__icontains=search)
        if category_slug := params.get("category"):
            qs = qs.filter(category__slug=category_slug)
        if status_filter := params.get("status"):
            qs = qs.filter(status=status_filter)
        if goal_min := params.get("goal_min"):
            qs = qs.filter(goal_amount__gte=goal_min)
        if goal_max := params.get("goal_max"):
            qs = qs.filter(goal_amount__lte=goal_max)
        if country := params.get("location_country"):
            qs = qs.filter(location_country=country)

        ordering = params.get("ordering", "-created_at")
        allowed_orderings = {"created_at", "-created_at", "raised_amount", "-raised_amount", "goal_amount", "-goal_amount"}
        if ordering in allowed_orderings:
            qs = qs.order_by(ordering)

        return qs

    def perform_create(self, serializer):
        campaign = services.create_campaign(created_by=self.request.user, **serializer.validated_data)
        serializer.instance = campaign

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.status != "draft":
            raise ValidationError("Only draft campaigns can be edited.")
        serializer.save()

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        campaign = self.get_object()
        try:
            services.submit_campaign_for_verification(campaign=campaign, actor=request.user)
        except DjangoPermissionDenied as exc:
            raise PermissionDenied(str(exc))
        except ValueError as exc:
            raise ValidationError(str(exc))
        return Response(CampaignDetailSerializer(campaign).data)

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        campaign = self.get_object()
        try:
            services.archive_campaign(campaign=campaign, actor=request.user)
        except DjangoPermissionDenied as exc:
            raise PermissionDenied(str(exc))
        return Response(CampaignDetailSerializer(campaign).data)


class BeneficiaryViewSet(viewsets.ModelViewSet):
    queryset = Beneficiary.objects.select_related("campaign")
    serializer_class = BeneficiarySerializer
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_permissions(self):
        if self.action in ("create", "partial_update"):
            return [IsAuthenticated(), IsNGO()]
        if self.action == "verify":
            return [IsAuthenticated(), IsInstitutionOrAdmin()]
        return [AllowAny()]

    def get_queryset(self):
        qs = super().get_queryset()
        if campaign_id := self.request.query_params.get("campaign"):
            qs = qs.filter(campaign_id=campaign_id)
        return qs

    def perform_create(self, serializer):
        campaign = serializer.validated_data["campaign"]
        if campaign.created_by_id != self.request.user.id:
            raise PermissionDenied("You can only add beneficiaries to your own campaigns.")
        serializer.save()

    @action(detail=True, methods=["post"])
    def verify(self, request, pk=None):
        beneficiary = self.get_object()
        new_status = request.data.get("status")
        try:
            services.verify_beneficiary(beneficiary=beneficiary, reviewer=request.user, status=new_status)
        except ValueError as exc:
            raise ValidationError(str(exc))
        return Response(BeneficiarySerializer(beneficiary).data)


class VerificationViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Reviews are created here (the actual approve/reject/more-info
    action); Campaign.status transitions happen as a side effect inside
    services.review_campaign(), never directly."""

    queryset = Verification.objects.select_related("campaign", "verified_by")
    serializer_class = VerificationSerializer
    permission_classes = [IsAuthenticated, IsInstitutionOrAdmin]

    def get_queryset(self):
        qs = super().get_queryset()
        if campaign_id := self.request.query_params.get("campaign"):
            qs = qs.filter(campaign_id=campaign_id)
        if status_filter := self.request.query_params.get("status"):
            qs = qs.filter(status=status_filter)
        return qs

    def create(self, request, *args, **kwargs):
        campaign = get_object_or_404(Campaign, pk=request.data.get("campaign"))
        try:
            verification = services.review_campaign(
                campaign=campaign,
                reviewer=request.user,
                status=request.data.get("status"),
                notes=request.data.get("notes", ""),
            )
        except ValueError as exc:
            raise ValidationError(str(exc))
        return Response(VerificationSerializer(verification).data, status=status.HTTP_201_CREATED)


class TransparencyLogViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Public, read-only — system-generated only (see models.py)."""

    queryset = TransparencyLog.objects.select_related("campaign")
    serializer_class = TransparencyLogSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        if campaign_id := self.request.query_params.get("campaign"):
            qs = qs.filter(campaign_id=campaign_id)
        return qs
