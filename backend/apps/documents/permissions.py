from rest_framework.permissions import BasePermission


class IsAuthenticatedForWrite(BasePermission):
    """View-level gate only — real scope/ownership checks happen in
    services.py. Documents are never publicly listable without auth at
    all (unlike Milestones/CampaignUpdates), since some scopes
    (beneficiary — government ID) are personal data, not public
    evidence; the queryset itself narrows what an authenticated user can
    see based on role, handled in views.py."""

    def has_permission(self, request, view) -> bool:
        return bool(request.user and request.user.is_authenticated)
