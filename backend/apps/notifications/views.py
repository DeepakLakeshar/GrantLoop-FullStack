from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .permissions import NotificationPermission, IsNotificationOwner
from .serializers import NotificationDetailSerializer, NotificationListSerializer
from . import services


class NotificationViewSet(viewsets.ViewSet):
    """
    ViewSet for managing user notifications.
    Delegates all queries and mutations to the services layer.
    """

    permission_classes = [NotificationPermission, IsNotificationOwner]

    def list(self, request):
        """
        GET /notifications/
        Lists all active non-deleted notifications for the current authenticated user.
        """
        notifications = services.list_notifications(user=request.user)
        serializer = NotificationListSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="unread-count")
    def unread_count(self, request):
        """
        GET /notifications/unread-count/
        Returns the unread notifications count for badge displays.
        """
        count = services.count_unread_notifications(user=request.user)
        return Response({"count": count}, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """
        GET /notifications/{id}/
        Fetches the detailed contents of a notification.
        Enforces object ownership constraints.
        """
        try:
            notification = services.get_notification(notification_id=pk)
        except Exception:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, notification)
        serializer = NotificationDetailSerializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        """
        POST /notifications/{id}/mark-read/
        Marks a single notification as read.
        Enforces object ownership constraints.
        """
        try:
            notification = services.get_notification(notification_id=pk)
        except Exception:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, notification)
        updated_notification = services.mark_as_read(notification=notification)
        serializer = NotificationDetailSerializer(updated_notification)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="mark-all-read")
    def mark_all_read(self, request):
        """
        POST /notifications/mark-all-read/
        Marks all active notifications as read.
        """
        updated_count = services.mark_all_as_read(user=request.user)
        return Response({"updated_count": updated_count}, status=status.HTTP_200_OK)
