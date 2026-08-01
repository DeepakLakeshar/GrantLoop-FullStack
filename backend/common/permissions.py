"""
RBAC foundation — scaffolded now, used by every business module built in
later phases. No business endpoint exists yet in Backend Phase 1, so
nothing below is wired to a view yet; this establishes the pattern so
later phases don't each invent their own role-check convention.
"""
from rest_framework.permissions import BasePermission


class HasRole(BasePermission):
    """Usage: permission_classes = [HasRole.for_roles("institution", "admin")]"""

    allowed_roles: tuple[str, ...] = ()

    def has_permission(self, request, view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in self.allowed_roles
        )

    @classmethod
    def for_roles(cls, *roles: str) -> type["HasRole"]:
        return type("HasRoleDynamic", (cls,), {"allowed_roles": roles})


class IsAdmin(HasRole):
    allowed_roles = ("admin",)


class IsInstitution(HasRole):
    allowed_roles = ("institution",)


class IsInstitutionOrAdmin(HasRole):
    allowed_roles = ("institution", "admin")


class IsNGO(HasRole):
    allowed_roles = ("ngo",)


class IsOwnerNGOOrAdmin(BasePermission):
    """Object-level: the NGO that created the campaign, or an admin.
    Used for campaign mutation — an NGO edits only its own campaigns."""

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.role == "admin":
            return True
        return user.role == "ngo" and obj.created_by_id == user.id
