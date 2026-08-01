from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.campaigns.models import Campaign, TransparencyLog
from apps.milestones.models import Milestone

User = get_user_model()


def make_user(email, role, full_name="Test User"):
    return User.objects.create_user(email=email, password="correcthorse8", role=role, full_name=full_name)


class MilestoneCRUDTests(APITestCase):
    def setUp(self):
        self.ngo = make_user("ngo@example.com", "ngo", "WaterHelp")
        self.other_ngo = make_user("other@example.com", "ngo", "Other NGO")
        self.institution = make_user("inst@example.com", "institution", "Global Trust")
        self.donor = make_user("donor@example.com", "donor", "Sarah Chen")
        self.campaign = Campaign.objects.create(created_by=self.ngo, title="Water Project", goal_amount=1000, status="live")

    def authenticate(self, user):
        response = self.client.post(reverse("auth-login"), {"email": user.email, "password": "correcthorse8"})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def test_anyone_can_list_milestones(self):
        Milestone.objects.create(campaign=self.campaign, title="Phase 1", target_amount=100)
        response = self.client.get(reverse("milestone-list"), {"campaign": str(self.campaign.id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owning_ngo_can_create_milestone(self):
        self.authenticate(self.ngo)
        response = self.client.post(reverse("milestone-list"), {
            "campaign": str(self.campaign.id), "title": "Site survey", "target_amount": "5000.00",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertTrue(TransparencyLog.objects.filter(campaign=self.campaign, action__icontains="created").exists())

    def test_other_ngo_cannot_create_milestone(self):
        self.authenticate(self.other_ngo)
        response = self.client.post(reverse("milestone-list"), {
            "campaign": str(self.campaign.id), "title": "Should fail", "target_amount": "100.00",
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_institution_can_create_milestone(self):
        self.authenticate(self.institution)
        response = self.client.post(reverse("milestone-list"), {
            "campaign": str(self.campaign.id), "title": "Institution-added", "target_amount": "100.00",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_donor_cannot_create_milestone(self):
        self.authenticate(self.donor)
        response = self.client.post(reverse("milestone-list"), {
            "campaign": str(self.campaign.id), "title": "Should fail", "target_amount": "100.00",
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_cannot_create_milestone(self):
        response = self.client.post(reverse("milestone-list"), {
            "campaign": str(self.campaign.id), "title": "Should fail", "target_amount": "100.00",
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_target_amount_must_be_positive(self):
        self.authenticate(self.ngo)
        response = self.client.post(reverse("milestone-list"), {
            "campaign": str(self.campaign.id), "title": "Bad", "target_amount": "-5.00",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_only_owning_ngo_or_institution_can_delete(self):
        milestone = Milestone.objects.create(campaign=self.campaign, title="Deletable", target_amount=100)
        self.authenticate(self.other_ngo)
        response = self.client.delete(reverse("milestone-detail", args=[milestone.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class MilestoneStatusTransitionTests(APITestCase):
    def setUp(self):
        self.ngo = make_user("ngo2@example.com", "ngo", "NGO Two")
        self.campaign = Campaign.objects.create(created_by=self.ngo, title="Transition Test", goal_amount=1000, status="live")
        self.milestone = Milestone.objects.create(campaign=self.campaign, title="Step 1", target_amount=500)

    def authenticate(self, user):
        response = self.client.post(reverse("auth-login"), {"email": user.email, "password": "correcthorse8"})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def test_pending_to_in_progress(self):
        self.authenticate(self.ngo)
        response = self.client.post(reverse("milestone-transition", args=[self.milestone.id]), {"status": "in_progress"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.milestone.refresh_from_db()
        self.assertEqual(self.milestone.status, "in_progress")
        self.assertIsNone(self.milestone.completed_at)

    def test_in_progress_to_completed_sets_completed_at(self):
        self.milestone.status = "in_progress"
        self.milestone.save()
        self.authenticate(self.ngo)
        response = self.client.post(reverse("milestone-transition", args=[self.milestone.id]), {"status": "completed"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.milestone.refresh_from_db()
        self.assertEqual(self.milestone.status, "completed")
        self.assertIsNotNone(self.milestone.completed_at)

    def test_cannot_skip_pending_to_completed(self):
        self.authenticate(self.ngo)
        response = self.client.post(reverse("milestone-transition", args=[self.milestone.id]), {"status": "completed"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_transition_out_of_completed(self):
        self.milestone.status = "completed"
        self.milestone.save()
        self.authenticate(self.ngo)
        response = self.client.post(reverse("milestone-transition", args=[self.milestone.id]), {"status": "in_progress"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class MilestoneReorderTests(APITestCase):
    def test_reorder_updates_order_field(self):
        ngo = make_user("ngo3@example.com", "ngo", "NGO Three")
        campaign = Campaign.objects.create(created_by=ngo, title="Reorder Test", goal_amount=1000, status="live")
        m1 = Milestone.objects.create(campaign=campaign, title="First", target_amount=100, order=0)
        m2 = Milestone.objects.create(campaign=campaign, title="Second", target_amount=100, order=1)

        response = self.client.post(reverse("auth-login"), {"email": ngo.email, "password": "correcthorse8"})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

        response = self.client.post(reverse("milestone-reorder"), {
            "campaign": str(campaign.id), "ordered_ids": [str(m2.id), str(m1.id)],
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        m1.refresh_from_db()
        m2.refresh_from_db()
        self.assertEqual(m2.order, 0)
        self.assertEqual(m1.order, 1)
