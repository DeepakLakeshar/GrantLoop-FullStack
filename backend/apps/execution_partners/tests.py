from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import ExecutionPartner

User = get_user_model()


def make_user(email, role, full_name="Test User"):
    return User.objects.create_user(email=email, password="correcthorse8", role=role, full_name=full_name)


class ExecutionPartnerAPITests(APITestCase):
    def setUp(self):
        self.admin = make_user("admin@example.com", "admin", "Admin User")
        self.ngo = make_user("ngo@example.com", "ngo", "NGO User")
        self.donor = make_user("donor@example.com", "donor", "Donor User")

        self.partner_user_1 = make_user("ep1@example.com", "execution_partner", "Partner User One")
        self.partner_user_2 = make_user("ep2@example.com", "execution_partner", "Partner User Two")

        self.partner_1 = ExecutionPartner.objects.create(
            user=self.partner_user_1,
            organization="Partner Org One",
            verification_status="verified"
        )

    def authenticate(self, user):
        response = self.client.post(reverse("auth-login"), {"email": user.email, "password": "correcthorse8"})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def test_anonymous_cannot_access_list(self):
        response = self.client.get(reverse("execution-partner-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_cannot_access_detail(self):
        response = self.client.get(reverse("execution-partner-detail", args=[self.partner_1.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_list_partners(self):
        self.authenticate(self.donor)
        response = self.client.get(reverse("execution-partner-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"] if "results" in response.data else response.data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["organization"], "Partner Org One")

    def test_authenticated_user_can_retrieve_partner(self):
        self.authenticate(self.ngo)
        response = self.client.get(reverse("execution-partner-detail", args=[self.partner_1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["organization"], "Partner Org One")
        self.assertEqual(response.data["verification_status"], "verified")

    def test_admin_can_create_partner(self):
        self.authenticate(self.admin)
        response = self.client.post(reverse("execution-partner-list"), {
            "user": str(self.partner_user_2.id),
            "organization": "New Partner Org"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ExecutionPartner.objects.filter(organization="New Partner Org").exists())

    def test_non_admin_cannot_create_partner(self):
        self.authenticate(self.partner_user_1)
        response = self.client.post(reverse("execution-partner-list"), {
            "user": str(self.partner_user_2.id),
            "organization": "New Partner Org"
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_partner_for_user_already_having_profile_fails(self):
        self.authenticate(self.admin)
        # partner_user_1 already has partner_1 profile
        response = self.client.post(reverse("execution-partner-list"), {
            "user": str(self.partner_user_1.id),
            "organization": "Duplicate Org"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partner_owner_patch_denied_by_view_permissions(self):
        """
        The default ExecutionPartnerPermission restricts write operations
        (POST, PATCH) strictly to admin-role users. The partner owner gets
        a 403 Forbidden response.
        """
        self.authenticate(self.partner_user_1)
        response = self.client.patch(reverse("execution-partner-detail", args=[self.partner_1.id]), {
            "organization": "Updated Partner Org"
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_organization(self):
        self.authenticate(self.admin)
        response = self.client.patch(reverse("execution-partner-detail", args=[self.partner_1.id]), {
            "organization": "Updated Partner Org"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.partner_1.refresh_from_db()
        self.assertEqual(self.partner_1.organization, "Updated Partner Org")

    def test_admin_cannot_update_verification_status_via_patch(self):
        """
        Since verification_status is excluded from the fields list of
        ExecutionPartnerWriteSerializer, any attempts to PATCH it are
        silently ignored by the serializer validation, preserving status.
        """
        self.authenticate(self.admin)
        response = self.client.patch(reverse("execution-partner-detail", args=[self.partner_1.id]), {
            "verification_status": "suspended"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.partner_1.refresh_from_db()
        self.assertEqual(self.partner_1.verification_status, "verified")

    def test_non_owner_partner_cannot_update(self):
        self.authenticate(self.partner_user_2)
        response = self.client.patch(reverse("execution-partner-detail", args=[self.partner_1.id]), {
            "organization": "Hack Attempts"
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_is_disabled(self):
        self.authenticate(self.admin)
        response = self.client.put(reverse("execution-partner-detail", args=[self.partner_1.id]), {
            "organization": "Not Allowed"
        })
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_is_disabled(self):
        self.authenticate(self.admin)
        response = self.client.delete(reverse("execution-partner-detail", args=[self.partner_1.id]))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
