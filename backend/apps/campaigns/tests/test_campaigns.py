from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.campaigns.models import Campaign, Category, TransparencyLog, Verification

User = get_user_model()


def make_user(email, role, full_name="Test User"):
    return User.objects.create_user(email=email, password="correcthorse8", role=role, full_name=full_name)


class CategoryTests(APITestCase):
    def test_category_list_is_public(self):
        Category.objects.create(name="Clean Water", slug="clean-water")
        response = self.client.get(reverse("category-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"] if "results" in response.data else response.data), 1)


class CampaignCRUDTests(APITestCase):
    def setUp(self):
        self.ngo = make_user("ngo@example.com", "ngo", "WaterHelp International")
        self.donor = make_user("donor@example.com", "donor", "Sarah Chen")
        self.category = Category.objects.create(name="Clean Water", slug="clean-water")

    def authenticate(self, user):
        response = self.client.post(reverse("auth-login"), {"email": user.email, "password": "correcthorse8"})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def test_ngo_can_create_campaign(self):
        self.authenticate(self.ngo)
        response = self.client.post(reverse("campaign-list"), {
            "title": "Clean Water Initiative",
            "goal_amount": "50000.00",
            "campaign_currency": "USD",
            "category": str(self.category.id),
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        campaign = Campaign.objects.get(title="Clean Water Initiative")
        self.assertEqual(campaign.status, "draft")
        self.assertEqual(campaign.created_by, self.ngo)

    def test_donor_cannot_create_campaign(self):
        self.authenticate(self.donor)
        response = self.client.post(reverse("campaign-list"), {
            "title": "Should Fail", "goal_amount": "1000.00",
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_cannot_create_campaign(self):
        response = self.client.post(reverse("campaign-list"), {
            "title": "Should Fail", "goal_amount": "1000.00",
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_goal_amount_must_be_positive(self):
        self.authenticate(self.ngo)
        response = self.client.post(reverse("campaign-list"), {
            "title": "Bad Goal", "goal_amount": "-5.00",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_public_listing_excludes_draft_campaigns(self):
        Campaign.objects.create(created_by=self.ngo, title="Draft", goal_amount=100, status="draft")
        live = Campaign.objects.create(created_by=self.ngo, title="Live One", goal_amount=100, status="live")
        response = self.client.get(reverse("campaign-list"))
        titles = [c["title"] for c in response.data["results"]] if "results" in response.data else [c["title"] for c in response.data]
        self.assertIn(live.title, titles)
        self.assertNotIn("Draft", titles)

    def test_ngo_sees_own_draft_campaigns_with_mine_flag(self):
        Campaign.objects.create(created_by=self.ngo, title="My Draft", goal_amount=100, status="draft")
        self.authenticate(self.ngo)
        response = self.client.get(reverse("campaign-list"), {"mine": "true"})
        titles = [c["title"] for c in response.data["results"]] if "results" in response.data else [c["title"] for c in response.data]
        self.assertIn("My Draft", titles)

    def test_search_filters_by_title(self):
        Campaign.objects.create(created_by=self.ngo, title="Mangrove Restoration", goal_amount=100, status="live")
        Campaign.objects.create(created_by=self.ngo, title="School Supplies", goal_amount=100, status="live")
        response = self.client.get(reverse("campaign-list"), {"search": "Mangrove"})
        rows = response.data["results"] if "results" in response.data else response.data
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["title"], "Mangrove Restoration")

    def test_only_owner_ngo_can_edit_draft_campaign(self):
        # 404, not 403: another NGO has no visibility into this draft at
        # all (it's outside their queryset entirely), so the correct
        # response doesn't even confirm the campaign exists.
        other_ngo = make_user("other-ngo@example.com", "ngo", "Other NGO")
        campaign = Campaign.objects.create(created_by=self.ngo, title="Mine", goal_amount=100, status="draft")
        self.authenticate(other_ngo)
        response = self.client.patch(reverse("campaign-detail", args=[campaign.id]), {"title": "Hijacked"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_edit_non_draft_campaign(self):
        campaign = Campaign.objects.create(created_by=self.ngo, title="Live", goal_amount=100, status="live")
        self.authenticate(self.ngo)
        response = self.client.patch(reverse("campaign-detail", args=[campaign.id]), {"title": "Edited"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CampaignLifecycleTests(APITestCase):
    def setUp(self):
        self.ngo = make_user("ngo2@example.com", "ngo", "NGO Two")
        self.institution = make_user("inst@example.com", "institution", "Global Trust")
        self.campaign = Campaign.objects.create(created_by=self.ngo, title="Lifecycle Test", goal_amount=1000, status="draft")

    def authenticate(self, user):
        response = self.client.post(reverse("auth-login"), {"email": user.email, "password": "correcthorse8"})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def test_submit_transitions_to_pending_verification(self):
        self.authenticate(self.ngo)
        response = self.client.post(reverse("campaign-submit", args=[self.campaign.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.campaign.refresh_from_db()
        self.assertEqual(self.campaign.status, "pending_verification")
        self.assertTrue(TransparencyLog.objects.filter(campaign=self.campaign).exists())

    def test_institution_approval_makes_campaign_live(self):
        self.campaign.status = "pending_verification"
        self.campaign.save()
        self.authenticate(self.institution)
        response = self.client.post(reverse("verification-list"), {
            "campaign": str(self.campaign.id), "status": "approved", "notes": "Looks good",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.campaign.refresh_from_db()
        self.assertEqual(self.campaign.status, "live")
        self.assertTrue(Verification.objects.filter(campaign=self.campaign, status="approved").exists())

    def test_institution_rejection_marks_campaign_rejected(self):
        self.campaign.status = "pending_verification"
        self.campaign.save()
        self.authenticate(self.institution)
        response = self.client.post(reverse("verification-list"), {
            "campaign": str(self.campaign.id), "status": "rejected", "notes": "Incomplete evidence",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.campaign.refresh_from_db()
        self.assertEqual(self.campaign.status, "rejected")

    def test_ngo_cannot_review_own_campaign(self):
        self.campaign.status = "pending_verification"
        self.campaign.save()
        self.authenticate(self.ngo)
        response = self.client.post(reverse("verification-list"), {
            "campaign": str(self.campaign.id), "status": "approved",
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_review_a_draft_campaign(self):
        self.authenticate(self.institution)
        response = self.client.post(reverse("verification-list"), {
            "campaign": str(self.campaign.id), "status": "approved",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_can_archive_campaign(self):
        admin = make_user("admin@example.com", "admin", "Admin User")
        self.campaign.status = "live"
        self.campaign.save()
        self.authenticate(admin)
        response = self.client.post(reverse("campaign-archive", args=[self.campaign.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.campaign.refresh_from_db()
        self.assertEqual(self.campaign.status, "archived")

    def test_ngo_cannot_archive_campaign(self):
        self.authenticate(self.ngo)
        response = self.client.post(reverse("campaign-archive", args=[self.campaign.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)



class TransparencyLogTests(APITestCase):
    def test_log_is_publicly_readable(self):
        ngo = make_user("ngo4@example.com", "ngo", "NGO Four")
        campaign = Campaign.objects.create(created_by=ngo, title="Log Test", goal_amount=100, status="live")
        TransparencyLog.objects.create(campaign=campaign, action="Campaign created")
        response = self.client.get(reverse("transparency-log-list"), {"campaign": str(campaign.id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_log_cannot_be_created_via_api(self):
        ngo = make_user("ngo5@example.com", "ngo", "NGO Five")
        admin = make_user("admin2@example.com", "admin", "Admin Two")
        campaign = Campaign.objects.create(created_by=ngo, title="Immutable Log Test", goal_amount=100, status="live")
        response = self.client.post(reverse("auth-login"), {"email": admin.email, "password": "correcthorse8"})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        response = self.client.post(reverse("transparency-log-list"), {
            "campaign": str(campaign.id), "action": "Should not be allowed",
        })
        # No create action registered on this viewset at all — POST isn't
        # a supported method, regardless of role, including admin.
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
