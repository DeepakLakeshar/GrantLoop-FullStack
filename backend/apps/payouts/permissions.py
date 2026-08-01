from rest_framework import permissions


class PayoutPermission(permissions.BasePermission):
    """
    Role-based access rules for Payout endpoints:
    - Donors: Completely blocked (403 Forbidden on all operations).
    - NGOs: Authorized to create requests for own verified campaigns,
            view own campaign payouts, and cancel own pending requests.
            Blocked from calling administrative state transition actions.
    - Admins: Unrestricted view/cancel access and exclusive authorization
              over lifecycle transitions (approve, reject, process, complete, fail).
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        user_role = getattr(request.user, "role", None)
        if user_role not in ["ngo", "admin"]:
            return False  # Donors and unmapped roles have no access

        if view.action in ["approve", "reject", "process", "complete", "fail"]:
            return user_role == "admin"

        return True

    def has_object_permission(self, request, view, obj):
        user_role = getattr(request.user, "role", None)
        if user_role == "admin":
            return True

        if user_role == "ngo":
            if view.action in ["approve", "reject", "process", "complete", "fail"]:
                return False
            # NGO must own either the payout target or the linked campaign
            return obj.ngo_id == request.user.id or obj.campaign.created_by_id == request.user.id

        return False
