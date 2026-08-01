"""
Reusable DRF permission classes for Execution Partners — role-based
checks only. No ownership or object-level logic here (has_permission
only, never has_object_permission); that belongs to a later task.
"""
from rest_framework.permissions import SAFE_METHODS, BasePermission

from . import services


class ExecutionPartnerPermission(BasePermission):
    """View-level default for the main ExecutionPartner endpoint. Admin
    manages partners (create/update/archive). Any authenticated user may
    read. Anonymous users get no access at all — not even read — since
    this is internal operational data, not donor-facing transparency
    evidence like Milestones/CampaignUpdates."""

    def has_permission(self, request, view) -> bool:
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role == "admin"


class IsExecutionPartner(BasePermission):
    """Grants access only to users whose account role is
    'execution_partner'. A role check only — not an ownership check, not
    an object-level check. Use this to gate endpoints that only make
    sense for a partner account at all (e.g. "my assigned milestones")."""

    def has_permission(self, request, view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "execution_partner"
        )


class IsVerifiedExecutionPartner(BasePermission):
    """Grants access only to an execution_partner account whose own
    ExecutionPartner profile has verification_status='verified'. Looks up
    the requesting user's own profile via services.get_partner_for_user —
    still a role/status check on the requester, not an object-level check
    against whatever instance the view is operating on. Use this to gate
    actions a pending or suspended partner shouldn't be able to do yet
    (e.g. uploading milestone evidence, submitting completion)."""

    def has_permission(self, request, view) -> bool:
        if not (request.user and request.user.is_authenticated and request.user.role == "execution_partner"):
            return False
        partner = services.get_partner_for_user(request.user)
        return partner is not None and services.is_verified(partner)


class IsExecutionPartnerOwner(BasePermission):
    """Object-level: the requesting user must be the specific person the
    ExecutionPartner instance in question belongs to. Delegates to
    services.is_owner() rather than re-implementing the check, so
    ownership has exactly one definition shared with the service layer.
    Has no has_permission() override — DRF's default (allow) applies at
    that stage, and the real gate is has_object_permission(), evaluated
    once a specific instance is in play (e.g. via get_object() in a
    future ViewSet). Admins are not automatically included here on
    purpose: compose with an admin-role check at the view level if
    admin override should also apply for a given action, so each view
    stays explicit about whether that bypass exists."""

    def has_object_permission(self, request, view, obj) -> bool:
        return services.is_owner(actor=request.user, partner=obj)