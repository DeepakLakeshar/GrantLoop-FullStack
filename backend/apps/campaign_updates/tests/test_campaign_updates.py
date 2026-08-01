from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.campaigns.models import Campaign, TransparencyLog
from apps.campaign_updates.models import CampaignUpdate

User = get_user_model()


def make_user(email, role, full_name="Test User"):
    return User.objects.create_user(email=email, password="correcthorse8", role=role, full_name=full_name)


class CampaignUpdateTests(APITestCase):
    def setUp(self):
        self.ngo = make_user("ngo@example.com", "ngo", "WaterHelp")
        self.other_ngo = make_user("other@example.com", "ngo", "Other NGO")
        self.donor = make_user("donor@example.com", "donor", "Sarah Chen")
        self.campaign = Campaign.objects.create(created_by=self.ngo, title="Water Project", goal_amount=1000, status="live")

    def authenticate(self, user):
        response = self.client.post(reverse("auth-login"), {"email": user.email, "password": "correcthorse8"})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def test_public_can_read_updates_without_auth(self):
        CampaignUpdate.objects.create(campaign=self.campaign, posted_by=self.ngo, content="Progress made.")
        response = self.client.get(reverse("campaignupdate-list"), {"campaign": str(self.campaign.id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owning_ngo_can_post_update(self):
        self.authenticate(self.ngo)
        response = self.client.post(reverse("campaignupdate-list"), {
            "campaign": str(self.campaign.id), "content": "Panels installed.", "update_type": "progress",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data["posted_by_name"], "WaterHelp")
        self.assertTrue(TransparencyLog.objects.filter(campaign=self.campaign, action__icontains="Update posted").exists())

    def test_other_ngo_cannot_post_update(self):
        self.authenticate(self.other_ngo)
        response = self.client.post(reverse("campaignupdate-list"), {
            "campaign": str(self.campaign.id), "content": "Should fail",
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_donor_cannot_post_update(self):
        self.authenticate(self.donor)
        response = self.client.post(reverse("campaignupdate-list"), {
            "campaign": str(self.campaign.id), "content": "Should fail",
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_cannot_post_update(self):
        response = self.client.post(reverse("campaignupdate-list"), {
            "campaign": str(self.campaign.id), "content": "Should fail",
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_empty_content_rejected(self):
        self.authenticate(self.ngo)
        response = self.client.post(reverse("campaignupdate-list"), {
            "campaign": str(self.campaign.id), "content": "   ",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_edit_endpoint_exists(self):
        update = CampaignUpdate.objects.create(campaign=self.campaign, posted_by=self.ngo, content="Original")
        self.authenticate(self.ngo)
        response = self.client.patch(reverse("campaignupdate-detail", args=[update.id]), {"content": "Edited"})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_owning_ngo_can_delete_update(self):
        update = CampaignUpdate.objects.create(campaign=self.campaign, posted_by=self.ngo, content="Mistake")
        self.authenticate(self.ngo)
        response = self.client.delete(reverse("campaignupdate-detail", args=[update.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_other_ngo_cannot_delete_update(self):
        update = CampaignUpdate.objects.create(campaign=self.campaign, posted_by=self.ngo, content="Protected")
        self.authenticate(self.other_ngo)
        response = self.client.delete(reverse("campaignupdate-detail", args=[update.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
