from rest_framework.permissions import BasePermission


class NotificationPermission(BasePermission):
    """
    Ensures the requesting user is fully authenticated.
    """

    def has_permission(self, request, view) -> bool:
        return bool(request.user and request.user.is_authenticated)


class IsNotificationOwner(BasePermission):
    """
    Ensures that the notification's recipient is the authenticated user.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        return bool(obj.recipient == request.user)
