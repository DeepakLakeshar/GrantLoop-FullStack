from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Notification
from . import services

User = get_user_model()


def make_user(email, role, full_name="Test User"):
    return User.objects.create_user(email=email, password="correcthorse8", role=role, full_name=full_name)


class NotificationAPITests(APITestCase):
    """
    Integration tests covering the Notifications module.
    """

    def setUp(self):
        self.user_a = make_user("usera@example.com", "donor", "User A")
        self.user_b = make_user("userb@example.com", "donor", "User B")

        # Create base notifications for user A
        self.notif_a1 = services.create_notification(
            recipient=self.user_a,
            title="Campaign Update",
            message="Your campaign was updated",
            notification_type="campaign_update",
            action_url="https://example.com/campaigns/1",
        )
        self.notif_a2 = services.create_notification(
            recipient=self.user_a,
            title="General Message",
            message="Welcome to the platform",
            notification_type="general",
        )

        # Shift timestamps deterministically to verify descending ordering
        from datetime import timedelta
        from django.utils import timezone
        self.notif_a1.created_at = timezone.now() - timedelta(minutes=5)
        self.notif_a1.save(update_fields=["created_at"])

        # Create notification for user B
        self.notif_b1 = services.create_notification(
            recipient=self.user_b,
            title="Donation Received",
            message="You received a donation",
            notification_type="donation_received",
        )

    def authenticate(self, user):
        response = self.client.post(reverse("auth-login"), {"email": user.email, "password": "correcthorse8"})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    # --- ANONYMOUS ACCESS ---

    def test_anonymous_cannot_list_notifications(self):
        response = self.client.get(reverse("notification-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_cannot_retrieve_notification(self):
        response = self.client.get(reverse("notification-detail", args=[self.notif_a1.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- LISTING & ORDERING ---

    def test_user_can_list_own_notifications(self):
        self.authenticate(self.user_a)
        response = self.client.get(reverse("notification-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["title"], "General Message")
        self.assertNotIn("message", response.data[0])  # List serializer omits message

    def test_notifications_ordering_newest_first(self):
        self.authenticate(self.user_a)
        response = self.client.get(reverse("notification-list"))
        # We created notif_a1 first, then notif_a2. List should return a2 first.
        self.assertEqual(response.data[0]["id"], str(self.notif_a2.id))
        self.assertEqual(response.data[1]["id"], str(self.notif_a1.id))

    # --- RETRIEVAL & OWNERSHIP ---

    def test_user_can_retrieve_own_notification(self):
        self.authenticate(self.user_a)
        response = self.client.get(reverse("notification-detail", args=[self.notif_a1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Your campaign was updated")

    def test_user_cannot_retrieve_others_notification(self):
        self.authenticate(self.user_a)
        response = self.client.get(reverse("notification-detail", args=[self.notif_b1.id]))
        self.assertIn(response.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN])

    # --- MARK READ / MARK ALL READ ---

    def test_mark_as_read(self):
        self.authenticate(self.user_a)
        url = reverse("notification-mark-read", args=[self.notif_a1.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_read"])

        self.notif_a1.refresh_from_db()
        self.assertTrue(self.notif_a1.is_read)

    def test_mark_as_read_idempotent(self):
        self.authenticate(self.user_a)
        url = reverse("notification-mark-read", args=[self.notif_a1.id])
        self.client.post(url)

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_read"])

    def test_cannot_mark_others_notification_as_read(self):
        self.authenticate(self.user_a)
        url = reverse("notification-mark-read", args=[self.notif_b1.id])
        response = self.client.post(url)
        self.assertIn(response.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN])

    def test_mark_all_as_read(self):
        self.authenticate(self.user_a)
        response = self.client.post(reverse("notification-mark-all-read"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["updated_count"], 2)

        count_response = self.client.get(reverse("notification-unread-count"))
        self.assertEqual(count_response.data["count"], 0)

    def test_mark_all_as_read_when_no_unread(self):
        self.authenticate(self.user_a)
        self.client.post(reverse("notification-mark-all-read"))

        response = self.client.post(reverse("notification-mark-all-read"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["updated_count"], 0)

    # --- UNREAD BADGE COUNT ---

    def test_unread_count(self):
        self.authenticate(self.user_a)
        response = self.client.get(reverse("notification-unread-count"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    # --- BULK BROADCAST SERVICE ---

    def test_bulk_creation_service(self):
        recipients = [self.user_a, self.user_b]
        created = services.create_notifications(
            recipients=recipients,
            title="System Alert",
            message="Maintenance tonight",
            notification_type="general",
        )
        self.assertEqual(len(created), 2)

        notif_a = Notification.objects.filter(recipient=self.user_a, title="System Alert")
        self.assertTrue(notif_a.exists())

        notif_b = Notification.objects.filter(recipient=self.user_b, title="System Alert")
        self.assertTrue(notif_b.exists())
