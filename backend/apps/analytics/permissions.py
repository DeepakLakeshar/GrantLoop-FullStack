from rest_framework import permissions


class IsAdminForAnalytics(permissions.BasePermission):
    """
    Grants access exclusively to authenticated users with the 'admin' role.
    All unauthorized users receive 403 Forbidden.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) == "admin"
        )


class IsNGOForAnalytics(permissions.BasePermission):
    """
    Grants access exclusively to authenticated users with the 'ngo' role.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) == "ngo"
        )


class IsDonorForAnalytics(permissions.BasePermission):
    """
    Grants access exclusively to authenticated users with the 'donor' role.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) == "donor"
        )


class IsAuthenticatedForAnalytics(permissions.BasePermission):
    """
    Grants access to any authenticated user with a recognized role (admin, ngo, donor)
    to inspect scoped chart aggregations and public leaderboards.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) in ["admin", "ngo", "donor"]
        )
