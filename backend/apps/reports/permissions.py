from rest_framework import permissions


class CanAccessDonationReports(permissions.BasePermission):
    """
    Grants read access to authenticated Admin, NGO, and Donor users.
    Service layer guarantees exact row-level data scoping:
      - Admin: Platform-wide donations
      - NGO: Donations directed to NGO's campaigns
      - Donor: Personal contribution records
    All unauthenticated or unrecognized roles receive 403 Forbidden.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return getattr(request.user, "role", None) in ["admin", "ngo", "donor"]


class CanAccessNGOReports(permissions.BasePermission):
    """
    Grants access exclusively to Admin users (platform-wide NGO stats)
    and NGO users (personal performance and payout history).
    Donors and unauthorized users receive 403 Forbidden.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return getattr(request.user, "role", None) in ["admin", "ngo"]


class CanAccessFinancialReports(permissions.BasePermission):
    """
    Grants access exclusively to platform Admin users for system-wide
    accounting balance verification and revenue summary reports.
    NGOs, Donors, and unauthorized users receive 403 Forbidden.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return getattr(request.user, "role", None) == "admin"


class CanAccessOperationalReports(permissions.BasePermission):
    """
    Grants access to operational report feeds (Campaigns, Beneficiaries, Payouts, Audit logs).
    Admin users can review all platform entities; NGO users can review entities
    scoped strictly to their owned campaigns.
    Donors and unauthorized users receive 403 Forbidden.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return getattr(request.user, "role", None) in ["admin", "ngo"]
