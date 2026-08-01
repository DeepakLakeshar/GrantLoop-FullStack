from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied as DRFPermissionDenied
from rest_framework.response import Response

from apps.campaigns.models import Campaign

from . import services
from .models import CampaignUpdate
from .permissions import CanManageCampaignUpdates
from .serializers import CampaignUpdateSerializer


class CampaignUpdateViewSet(viewsets.ModelViewSet):
    """
    Updates are append-only once posted — no edit endpoint, only create
    and delete. This mirrors TransparencyLog's immutability: donors
    should be able to trust that an update they read wasn't quietly
    altered after the fact. A mistaken post gets deleted and reposted,
    not silently edited.
    """

    queryset = CampaignUpdate.objects.select_related("campaign", "posted_by").all()
    serializer_class = CampaignUpdateSerializer
    permission_classes = [CanManageCampaignUpdates]
    http_method_names = ["get", "post", "delete", "head", "options"]

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
            update = services.create_update(campaign=campaign, actor=request.user, **fields)
        except DjangoPermissionDenied as exc:
            raise DRFPermissionDenied(str(exc))
        return Response(self.get_serializer(update).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        update = self.get_object()
        try:
            services.delete_update(update=update, actor=request.user)
        except DjangoPermissionDenied as exc:
            raise DRFPermissionDenied(str(exc))
        return Response(status=status.HTTP_204_NO_CONTENT)
