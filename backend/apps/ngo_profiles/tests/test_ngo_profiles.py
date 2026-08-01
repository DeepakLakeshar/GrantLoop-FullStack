from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.ngo_profiles.models import NGOProfile

User = get_user_model()


def make_user(email, role, full_name="Test User"):
    return User.objects.create_user(email=email, password="correcthorse8", role=role, full_name=full_name)


class NGOProfileTests(APITestCase):
    def setUp(self):
        self.ngo = make_user("ngo@example.com", "ngo", "WaterHelp International")
        self.donor = make_user("donor@example.com", "donor", "Sarah Chen")

    def authenticate(self, user):
        response = self.client.post(reverse("auth-login"), {"email": user.email, "password": "correcthorse8"})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def test_ngo_get_creates_profile_on_first_access(self):
        self.authenticate(self.ngo)
        response = self.client.get(reverse("ngo-profile-mine"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["organization_name"], "WaterHelp International")
        self.assertTrue(NGOProfile.objects.filter(user=self.ngo).exists())

    def test_ngo_can_update_own_profile(self):
        self.authenticate(self.ngo)
        response = self.client.put(reverse("ngo-profile-mine"), {
            "organization_name": "WaterHelp International Trust",
            "description": "Providing clean water access since 2014.",
            "website_url": "https://waterhelp.example.org",
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["organization_name"], "WaterHelp International Trust")

    def test_donor_cannot_access_ngo_profile_mine_endpoint(self):
        self.authenticate(self.donor)
        response = self.client.get(reverse("ngo-profile-mine"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_cannot_access_ngo_profile_mine_endpoint(self):
        response = self.client.get(reverse("ngo-profile-mine"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_public_profile_is_readable_without_auth(self):
        profile = NGOProfile.objects.create(user=self.ngo, organization_name="Public NGO")
        response = self.client.get(reverse("ngo-profile-public", args=[self.ngo.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["organization_name"], "Public NGO")

    def test_public_profile_404_for_unknown_user(self):
        import uuid
        response = self.client.get(reverse("ngo-profile-public", args=[uuid.uuid4()]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
