from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied as DRFPermissionDenied, ValidationError
from rest_framework.permissions import AllowAny

from .models import Donation
from .serializers import (
    DonationDetailSerializer,
    DonationListSerializer,
    DonationWriteSerializer,
)
from . import services


class DonationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing, retrieving, and creating campaign donations.
    Enforces read-only fields on public endpoints, masks anonymous contributions,
    and delegates write transitions directly to the services layer.
    """
    queryset = Donation.objects.select_related("donor", "campaign").all()
    http_method_names = ["get", "post", "head", "options"]

    def get_permissions(self):
        """
        Retrieves list of permissions active for this request.
        Allows anyone to list, retrieve, and initiate checkout transactions.
        """
        return [AllowAny()]

    def get_queryset(self):
        """
        Retrieves the base pre-fetched donation queryset.
        """
        return super().get_queryset()

    def get_serializer_class(self):
        """
        Selects serializer representation depending on view action.
        """
        if self.action == "list":
            return DonationListSerializer
        if self.action == "retrieve":
            return DonationDetailSerializer
        return DonationWriteSerializer

    def perform_create(self, serializer):
        """
        Delegates the initiation of a donation session to the service layer.
        """
        campaign = serializer.validated_data.get("campaign")
        original_amount = serializer.validated_data.get("original_amount")
        original_currency = serializer.validated_data.get("original_currency")
        is_anonymous = serializer.validated_data.get("is_anonymous", False)

        # Authenticated user is mapped as donor, guest is mapped as None
        donor = self.request.user if self.request.user.is_authenticated else None

        try:
            donation = services.initiate_donation(
                campaign=campaign,
                donor=donor,
                original_amount=original_amount,
                original_currency=original_currency,
                is_anonymous=is_anonymous,
            )
            serializer.instance = donation
        except DjangoPermissionDenied as exc:
            raise DRFPermissionDenied(str(exc))
        except ValueError as exc:
            raise ValidationError(str(exc))
