from rest_framework.permissions import SAFE_METHODS, BasePermission
from .models import VerificationStatus


class BeneficiaryPermission(BasePermission):
    """
    Role-based and ownership-based access control gates for beneficiaries.

    Permission matrix:
      - Admin:             full access to everything (list/detail/create/update/delete/verify/reject)
      - NGO:               create beneficiaries for own campaigns; read/update own-campaign records
      - Donor:             read verified beneficiaries only
      - Execution Partner: read beneficiaries on campaigns linked via milestones
      - Anonymous:         denied
    """

    def has_permission(self, request, view) -> bool:
        # Deny anonymous access
        if not (request.user and request.user.is_authenticated):
            return False

        # Admins bypass all permission gates
        if request.user.role == "admin":
            return True

        if request.method in SAFE_METHODS:
            return True

        if request.method == "POST":
            # NGOs can create beneficiaries; verify/reject actions are POST too
            # but those are handled by get_object() → has_object_permission, so allow
            return request.user.role == "ngo"

        # PATCH / DELETE / PUT – require authentication (ownership checked at object level)
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # Admin has absolute access
        if user.role == "admin":
            return True

        # Write operations
        if request.method not in SAFE_METHODS:
            if request.method == "DELETE":
                return False  # Only admins can delete (admin already handled above)
            # NGOs can modify their own campaign beneficiaries
            return user.role == "ngo" and obj.campaign.created_by_id == user.id

        # Safe read checks
        if user.role == "ngo":
            return obj.campaign.created_by_id == user.id

        if user.role == "donor":
            return obj.verification_status == VerificationStatus.VERIFIED

        if user.role == "execution_partner":
            return obj.campaign.milestones.filter(execution_partner__user=user).exists()

        return False
