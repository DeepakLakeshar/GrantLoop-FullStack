from rest_framework.permissions import SAFE_METHODS, BasePermission


class CanManageCampaignUpdates(BasePermission):
    """Public read (updates are part of the transparency timeline).
    Write requires authentication; the real owning-NGO-or-admin check
    happens in services.py against the specific campaign."""

    def has_permission(self, request, view) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)
