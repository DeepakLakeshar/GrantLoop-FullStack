from rest_framework.permissions import SAFE_METHODS, BasePermission


class CanManageCampaignMilestones(BasePermission):
    """View-level gate: must be authenticated to write at all. The real
    ownership/role check (owning NGO, institution, or admin) happens in
    services.py against the specific campaign — this class only rules
    out anonymous writes and lets GET through for everyone, since
    milestones are public evidence of progress."""

    def has_permission(self, request, view) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)
