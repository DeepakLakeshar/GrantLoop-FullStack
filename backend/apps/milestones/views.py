from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied as DRFPermissionDenied
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied

from apps.campaigns.models import Campaign

from . import services
from .models import Milestone
from .permissions import CanManageCampaignMilestones
from .serializers import (
    MilestoneReorderSerializer,
    MilestoneSerializer,
    MilestoneStatusTransitionSerializer,
)
from grantloop.openapi import milestone_viewset_schema


@milestone_viewset_schema
class MilestoneViewSet(viewsets.ModelViewSet):
    """
    Milestones are public evidence of campaign progress (readable by
    anyone), but writes are gated: owning NGO, institution, or admin only
    — enforced in services.py, not here (this view only orchestrates).
    """

    queryset = Milestone.objects.select_related("campaign").all()
    serializer_class = MilestoneSerializer
    permission_classes = [CanManageCampaignMilestones]

    def get_queryset(self):
        qs = super().get_queryset()
        campaign_id = self.request.query_params.get("campaign")
        if campaign_id:
            qs = qs.filter(campaign_id=campaign_id)
        return qs

    def create(self, request, *args, **kwargs):
        campaign_id = request.data.get("campaign")
        campaign = get_object_or_404(Campaign, id=campaign_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        fields = {k: v for k, v in serializer.validated_data.items() if k != "campaign"}
        try:
            milestone = services.create_milestone(campaign=campaign, actor=request.user, **fields)
        except DjangoPermissionDenied as exc:
            raise DRFPermissionDenied(str(exc))
        return Response(self.get_serializer(milestone).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        milestone = self.get_object()
        if not services._can_manage_milestone(campaign=milestone.campaign, actor=request.user):
            raise DRFPermissionDenied("You don't have permission to edit this milestone.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        milestone = self.get_object()
        if not services._can_manage_milestone(campaign=milestone.campaign, actor=request.user):
            raise DRFPermissionDenied("You don't have permission to delete this milestone.")
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def transition(self, request, pk=None):
        milestone = self.get_object()
        serializer = MilestoneStatusTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            milestone = services.transition_status(
                milestone=milestone, actor=request.user, new_status=serializer.validated_data["status"]
            )
        except DjangoPermissionDenied as exc:
            raise DRFPermissionDenied(str(exc))
        except ValueError as exc:
            raise ValidationError(str(exc))
        return Response(self.get_serializer(milestone).data)

    @action(detail=False, methods=["post"], url_path="reorder")
    def reorder(self, request):
        campaign_id = request.data.get("campaign")
        campaign = get_object_or_404(Campaign, id=campaign_id)
        serializer = MilestoneReorderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            milestones = services.reorder_milestones(
                campaign=campaign, actor=request.user,
                ordered_ids=[str(i) for i in serializer.validated_data["ordered_ids"]],
            )
        except DjangoPermissionDenied as exc:
            raise DRFPermissionDenied(str(exc))
        except ValueError as exc:
            raise ValidationError(str(exc))
        return Response(self.get_serializer(milestones, many=True).data)
