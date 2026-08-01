from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.campaigns.models import TransparencyLog
from .models import Beneficiary, VerificationStatus
from .events import notify_beneficiary_verified, notify_beneficiary_rejected, notify_beneficiary_deleted


def get_beneficiary(*, beneficiary_id, user=None) -> Beneficiary:
    """
    Retrieves a single Beneficiary by ID.
    Non-admins are blocked from fetching soft-deleted items.
    """
    # Use standard manager (which filters out deleted by default) for normal users
    if user and user.role == "admin":
        queryset = Beneficiary.objects.all_with_deleted()
    else:
        queryset = Beneficiary.objects.all()

    try:
        return queryset.select_related("campaign", "campaign__created_by").get(id=beneficiary_id)
    except Beneficiary.DoesNotExist:
        raise ValidationError("Beneficiary not found.")


def list_beneficiaries(*, user) -> QuerySet:
    """
    Retrieves scoped QuerySet depending on the requesting user's role:
    - Admin: All records (including soft-deleted).
    - NGO: Beneficiaries of campaigns created by this user.
    - Donor: Verified beneficiaries only (non-deleted).
    - Partner: Linked campaign beneficiaries (linked through milestone assignments).
    """
    if user.role == "admin":
        return Beneficiary.objects.all_with_deleted().select_related("campaign", "campaign__created_by").order_by("-created_at")

    # Base active (non-deleted) queryset
    queryset = Beneficiary.objects.select_related("campaign", "campaign__created_by")

    if user.role == "ngo":
        queryset = queryset.filter(campaign__created_by=user)
    elif user.role == "donor":
        queryset = queryset.filter(verification_status=VerificationStatus.VERIFIED)
    elif user.role == "execution_partner":
        queryset = queryset.filter(campaign__milestones__execution_partner__user=user).distinct()
    else:
        queryset = queryset.none()

    return queryset.order_by("-created_at")



def create_beneficiary(
    *,
    user,
    campaign,
    full_name: str,
    email: str,
    phone_number: str,
    address: str,
    city: str,
    state: str,
    country: str,
    postal_code: str,
    government_id: str,
    date_of_birth=None,
    profile_photo=None,
) -> Beneficiary:
    """
    Creates a pending beneficiary.
    Validates role access (NGO owner of campaign) and database constraints.
    """
    if user.role != "ngo":
        raise PermissionDenied("Only NGO owners can create beneficiaries.")
    if campaign.created_by_id != user.id:
        raise PermissionDenied("You can only create beneficiaries for your own campaigns.")

    with transaction.atomic():
        if Beneficiary.objects.all_with_deleted().filter(government_id=government_id).exists():
            raise ValidationError({"government_id": "A beneficiary with this government ID already exists."})

        beneficiary = Beneficiary.objects.create(
            campaign=campaign,
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            address=address,
            city=city,
            state=state,
            country=country,
            postal_code=postal_code,
            date_of_birth=date_of_birth,
            government_id=government_id,
            profile_photo=profile_photo,
            verification_status=VerificationStatus.PENDING,
        )
    return beneficiary


def update_beneficiary(*, beneficiary_id: str, user, **kwargs) -> Beneficiary:
    """
    Atomically updates a beneficiary.
    Restricts update access and checks uniqueness.
    """
    with transaction.atomic():
        beneficiary = Beneficiary.objects.all_with_deleted().get(id=beneficiary_id)

        is_admin = user.role == "admin"
        is_owner = user.role == "ngo" and beneficiary.campaign.created_by_id == user.id
        if not (is_admin or is_owner):
            raise PermissionDenied("You do not have permission to modify this beneficiary.")

        # Strip status modification variables (handled exclusively by transition endpoints)
        kwargs.pop("verification_status", None)
        kwargs.pop("rejection_reason", None)
        kwargs.pop("verified_by", None)
        kwargs.pop("verified_at", None)
        kwargs.pop("rejected_by", None)
        kwargs.pop("rejected_at", None)

        gov_id = kwargs.get("government_id")
        if gov_id and gov_id != beneficiary.government_id:
            if Beneficiary.objects.all_with_deleted().filter(government_id=gov_id).exclude(id=beneficiary.id).exists():
                raise ValidationError({"government_id": "A beneficiary with this government ID already exists."})

        for field, value in kwargs.items():
            setattr(beneficiary, field, value)

        beneficiary.save()
    return beneficiary


def verify_beneficiary(*, beneficiary_id: str, user) -> Beneficiary:
    """
    Approves a beneficiary (Admin only).
    """
    if user.role != "admin":
        raise PermissionDenied("Only administrators can verify beneficiaries.")

    with transaction.atomic():
        beneficiary = Beneficiary.objects.all_with_deleted().get(id=beneficiary_id)

        if beneficiary.verification_status != VerificationStatus.PENDING:
            raise ValidationError("Cannot verify a beneficiary that is not pending.")

        beneficiary.verification_status = VerificationStatus.VERIFIED
        beneficiary.verified_by = user
        beneficiary.verified_at = timezone.now()
        beneficiary.rejection_reason = ""
        beneficiary.save(update_fields=["verification_status", "verified_by", "verified_at", "rejection_reason", "updated_at"])

        # Create audit timeline entry
        TransparencyLog.objects.create(
            campaign=beneficiary.campaign,
            action=f"Beneficiary '{beneficiary.full_name}' verified by admin.",
        )

        # Notify via decoupled events
        notify_beneficiary_verified(beneficiary)

    return beneficiary


def reject_beneficiary(*, beneficiary_id: str, user, rejection_reason: str) -> Beneficiary:
    """
    Rejects verification for a beneficiary (Admin only).
    """
    if user.role != "admin":
        raise PermissionDenied("Only administrators can reject beneficiaries.")
    if not rejection_reason or not rejection_reason.strip():
        raise ValidationError({"rejection_reason": "Rejection reason is required."})

    with transaction.atomic():
        beneficiary = Beneficiary.objects.all_with_deleted().get(id=beneficiary_id)

        if beneficiary.verification_status != VerificationStatus.PENDING:
            raise ValidationError("Cannot reject a beneficiary that is not pending.")

        beneficiary.verification_status = VerificationStatus.REJECTED
        beneficiary.rejected_by = user
        beneficiary.rejected_at = timezone.now()
        beneficiary.rejection_reason = rejection_reason
        beneficiary.save(update_fields=["verification_status", "rejected_by", "rejected_at", "rejection_reason", "updated_at"])

        # Create audit timeline entry
        TransparencyLog.objects.create(
            campaign=beneficiary.campaign,
            action=f"Beneficiary '{beneficiary.full_name}' verification rejected. Reason: {rejection_reason}.",
        )

        # Notify via decoupled events
        notify_beneficiary_rejected(beneficiary, rejection_reason)

    return beneficiary


def delete_beneficiary(*, beneficiary_id: str, user) -> None:
    """
    Performs soft deletion of a beneficiary (Admin only).
    """
    if user.role != "admin":
        raise PermissionDenied("Only administrators can delete beneficiaries.")

    with transaction.atomic():
        beneficiary = Beneficiary.objects.all_with_deleted().get(id=beneficiary_id)
        beneficiary.is_deleted = True
        beneficiary.save(update_fields=["is_deleted", "updated_at"])

        # Create audit timeline entry
        TransparencyLog.objects.create(
            campaign=beneficiary.campaign,
            action=f"Beneficiary '{beneficiary.full_name}' has been soft deleted.",
        )

        # Dispatch decoupled event
        notify_beneficiary_deleted(beneficiary)
