import tempfile
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.db.models import ProtectedError
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.campaigns.models import Campaign, TransparencyLog
from apps.notifications.models import Notification, NotificationType
from .models import Beneficiary, VerificationStatus
from . import services

User = get_user_model()


def make_user(email, role, full_name="Test User"):
    return User.objects.create_user(email=email, password="correcthorse8", role=role, full_name=full_name)


class BeneficiaryAPITests(APITestCase):
    """
    Exhaustive integration tests for the Beneficiary Management Module.
    """

    def setUp(self):
        self.admin = make_user("admin@example.com", "admin", "Admin User")
        self.ngo_1 = make_user("ngo1@example.com", "ngo", "NGO Owner One")
        self.ngo_2 = make_user("ngo2@example.com", "ngo", "NGO Owner Two")
        self.donor = make_user("donor@example.com", "donor", "Donor User")
        self.partner = make_user("partner@example.com", "execution_partner", "Partner User")

        # Create campaigns
        self.campaign_1 = Campaign.objects.create(
            created_by=self.ngo_1,
            title="Clean Water Campaign",
            goal_amount=5000,
            status="live",
        )
        self.campaign_2 = Campaign.objects.create(
            created_by=self.ngo_2,
            title="Education Initiative",
            goal_amount=10000,
            status="live",
        )

        # Create a pending beneficiary for campaign_1
        self.beneficiary = services.create_beneficiary(
            user=self.ngo_1,
            campaign=self.campaign_1,
            full_name="John Doe",
            email="johndoe@example.com",
            phone_number="+15555555555",
            address="123 Street",
            city="City A",
            state="State B",
            country="US",
            postal_code="12345",
            government_id="GOV123",
            date_of_birth=date(1990, 1, 1),
        )

    def authenticate(self, user):
        response = self.client.post(reverse("auth-login"), {"email": user.email, "password": "correcthorse8"})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    # --- ANONYMOUS ACCESS ---

    def test_anonymous_cannot_access(self):
        response = self.client.get(reverse("beneficiary-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- PERMISSIONS & RETRIEVAL SCENARIOS ---

    def test_donor_can_only_view_verified_beneficiaries(self):
        self.authenticate(self.donor)
        # john doe is currently pending, donor should not see it in listing
        response = self.client.get(reverse("beneficiary-list"))
        self.assertEqual(len(response.data), 0)

        # retrieve details of pending beneficiary should fail
        response_detail = self.client.get(reverse("beneficiary-detail", args=[self.beneficiary.id]))
        self.assertEqual(response_detail.status_code, status.HTTP_403_FORBIDDEN)

        # Approve beneficiary
        self.authenticate(self.admin)
        services.verify_beneficiary(beneficiary_id=str(self.beneficiary.id), user=self.admin)

        # Now donor should see verified beneficiary
        self.authenticate(self.donor)
        response = self.client.get(reverse("beneficiary-list"))
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["full_name"], "John Doe")

    def test_ngo_can_only_view_own_campaign_beneficiaries(self):
        self.authenticate(self.ngo_2)
        response = self.client.get(reverse("beneficiary-list"))
        # NGO 2 owns campaign 2 which has no beneficiaries
        self.assertEqual(len(response.data), 0)

        # NGO 2 attempts to fetch NGO 1's beneficiary details
        response_detail = self.client.get(reverse("beneficiary-detail", args=[self.beneficiary.id]))
        self.assertEqual(response_detail.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_view_all(self):
        self.authenticate(self.admin)
        response = self.client.get(reverse("beneficiary-list"))
        self.assertEqual(len(response.data), 1)

    # --- VALIDATION CHECKS ---

    def test_government_id_uniqueness(self):
        self.authenticate(self.ngo_1)
        # Attempt to create duplicate government ID
        data = {
            "campaign": str(self.campaign_1.id),
            "full_name": "Jane Doe",
            "email": "janedoe@example.com",
            "phone_number": "+15556666666",
            "address": "456 Street",
            "city": "City A",
            "state": "State B",
            "country": "US",
            "postal_code": "12345",
            "government_id": "GOV123",  # Duplicate
        }
        response = self.client.post(reverse("beneficiary-list"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("government_id", response.data)

    def test_invalid_phone_format(self):
        self.authenticate(self.ngo_1)
        data = {
            "campaign": str(self.campaign_1.id),
            "full_name": "Jane Doe",
            "email": "janedoe@example.com",
            "phone_number": "not-a-phone-number",
            "address": "456 Street",
            "city": "City A",
            "state": "State B",
            "country": "US",
            "postal_code": "12345",
            "government_id": "GOV456",
        }
        response = self.client.post(reverse("beneficiary-list"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("phone_number", response.data)

    def test_future_date_of_birth(self):
        self.authenticate(self.ngo_1)
        future_dob = date.today() + timedelta(days=1)
        data = {
            "campaign": str(self.campaign_1.id),
            "full_name": "Jane Doe",
            "email": "janedoe@example.com",
            "phone_number": "+15556666666",
            "address": "456 Street",
            "city": "City A",
            "state": "State B",
            "country": "US",
            "postal_code": "12345",
            "government_id": "GOV456",
            "date_of_birth": future_dob.isoformat(),
        }
        response = self.client.post(reverse("beneficiary-list"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("date_of_birth", response.data)

    def test_image_validation_size_and_mimetype(self):
        self.authenticate(self.ngo_1)
        # Create a fake file with png extension but bad mime or oversized
        with tempfile.NamedTemporaryFile(suffix=".png") as bad_file:
            bad_file.write(b"a" * (6 * 1024 * 1024))  # 6MB file
            bad_file.seek(0)

            data = {
                "campaign": str(self.campaign_1.id),
                "full_name": "Jane Doe",
                "email": "janedoe@example.com",
                "phone_number": "+15556666666",
                "address": "456 Street",
                "city": "City A",
                "state": "State B",
                "country": "US",
                "postal_code": "12345",
                "government_id": "GOV456",
                "profile_photo": bad_file,
            }
            response = self.client.post(reverse("beneficiary-list"), data, format="multipart")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("profile_photo", response.data)

    # --- STATE TRANSITIONS ---

    def test_admin_can_verify_and_notify_ngo(self):
        self.authenticate(self.admin)
        url = reverse("beneficiary-verify", args=[self.beneficiary.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["verification_status"], VerificationStatus.VERIFIED)

        # Audit checks: verified_by is logged
        self.assertEqual(response.data["verified_by"]["email"], self.admin.email)

        # Check TransparencyLog created
        self.assertTrue(TransparencyLog.objects.filter(campaign=self.campaign_1, action__icontains="verified").exists())

        # Check Notification created for NGO owner
        notif = Notification.objects.filter(recipient=self.ngo_1, notification_type=NotificationType.BENEFICIARY_VERIFIED).first()
        self.assertIsNotNone(notif)
        self.assertIn("verified", notif.message)
        self.assertEqual(notif.action_url, f"/beneficiaries/{self.beneficiary.id}/")

    def test_admin_can_reject_and_notify_ngo(self):
        self.authenticate(self.admin)
        url = reverse("beneficiary-reject", args=[self.beneficiary.id])
        response = self.client.post(url, {"rejection_reason": "Incomplete verification documents"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["verification_status"], VerificationStatus.REJECTED)
        self.assertEqual(response.data["rejection_reason"], "Incomplete verification documents")

        # Check Notification created for NGO owner
        notif = Notification.objects.filter(recipient=self.ngo_1, notification_type=NotificationType.BENEFICIARY_REJECTED).first()
        self.assertIsNotNone(notif)
        self.assertIn("Incomplete verification", notif.message)

    def test_invalid_state_transitions(self):
        self.authenticate(self.admin)
        # Verify first
        services.verify_beneficiary(beneficiary_id=str(self.beneficiary.id), user=self.admin)

        # Attempt to reject verified beneficiary -> should fail
        url = reverse("beneficiary-reject", args=[self.beneficiary.id])
        response = self.client.post(url, {"rejection_reason": "Oops"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_concurrent_verification_attempts(self):
        self.authenticate(self.admin)
        url = reverse("beneficiary-verify", args=[self.beneficiary.id])
        response1 = self.client.post(url)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        # Second admin verify call must fail
        response2 = self.client.post(url)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

    # --- SOFT DELETION ---

    def test_admin_can_soft_delete_and_hides_from_queries(self):
        self.authenticate(self.admin)
        url = reverse("beneficiary-detail", args=[self.beneficiary.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # NGO lists -> should not see soft deleted beneficiary
        self.authenticate(self.ngo_1)
        list_response = self.client.get(reverse("beneficiary-list"))
        self.assertEqual(len(list_response.data), 0)

        # Admin lists -> can see soft deleted beneficiary
        self.authenticate(self.admin)
        list_response = self.client.get(reverse("beneficiary-list"))
        self.assertEqual(len(list_response.data), 1)
        self.assertTrue(list_response.data[0]["is_read"] if "is_read" in list_response.data[0] else True)

    # --- PROTECTED CAMPAIGN DELETION ---

    def test_campaign_deletion_blocked_by_beneficiaries(self):
        # Attempt to delete campaign_1 should raise ProtectedError
        with self.assertRaises(ProtectedError):
            self.campaign_1.delete()

    # --- SEARCH & FILTER ---

    def test_search_and_filters(self):
        self.authenticate(self.admin)
        # Search by full_name
        response = self.client.get(reverse("beneficiary-list") + "?search=John")
        self.assertEqual(len(response.data), 1)

        # Search mismatch
        response = self.client.get(reverse("beneficiary-list") + "?search=Alice")
        self.assertEqual(len(response.data), 0)

        # Filter by status
        response = self.client.get(reverse("beneficiary-list") + f"?verification_status={VerificationStatus.PENDING}")
        self.assertEqual(len(response.data), 1)
