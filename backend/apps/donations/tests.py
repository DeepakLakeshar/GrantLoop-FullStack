from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.campaigns.models import Campaign, Category
from .models import Donation
from . import services

User = get_user_model()


def make_user(email, role, full_name="Test User"):
    return User.objects.create_user(email=email, password="correcthorse8", role=role, full_name=full_name)


class DonationAPITests(APITestCase):
    """
    Exhaustive integration test suite for the Donation module.
    Covers view-level access controls, creation constraints, service transitions,
    concurrency/idempotency rules, serializer masking, and querying.
    """

    def setUp(self):
        # Seed user roles
        self.ngo = make_user("ngo@example.com", "ngo", "NGO User")
        self.donor = make_user("donor@example.com", "donor", "Donor User")

        # Seed categories and campaigns
        self.category = Category.objects.create(name="Education", slug="education")

        self.live_campaign = Campaign.objects.create(
            title="Help Education",
            description="Providing books",
            goal_amount=10000,
            campaign_currency="INR",
            status="live",
            category=self.category,
            created_by=self.ngo,
        )

        self.draft_campaign = Campaign.objects.create(
            title="Draft Campaign",
            description="Drafting",
            goal_amount=5000,
            campaign_currency="INR",
            status="draft",
            category=self.category,
            created_by=self.ngo,
        )

    def authenticate(self, user):
        response = self.client.post(reverse("auth-login"), {"email": user.email, "password": "correcthorse8"})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    # --- AUTHENTICATION & PERMISSIONS TESTS ---

    def test_anonymous_user_can_create_donation(self):
        url = reverse("donation-list")
        data = {
            "campaign": str(self.live_campaign.id),
            "original_amount": "100.00",
            "original_currency": "INR",
            "is_anonymous": True,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        donation = Donation.objects.get(id=response.data["id"])
        self.assertIsNone(donation.donor)

    def test_authenticated_user_can_create_donation(self):
        self.authenticate(self.donor)
        url = reverse("donation-list")
        data = {
            "campaign": str(self.live_campaign.id),
            "original_amount": "200.00",
            "original_currency": "INR",
            "is_anonymous": False,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        donation = Donation.objects.get(id=response.data["id"])
        self.assertEqual(donation.donor, self.donor)

    def test_anonymous_user_can_list_donations(self):
        services.initiate_donation(
            campaign=self.live_campaign,
            donor=self.donor,
            original_amount=100,
            original_currency="INR",
        )
        url = reverse("donation-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_user_can_retrieve_donation(self):
        donation = services.initiate_donation(
            campaign=self.live_campaign,
            donor=self.donor,
            original_amount=100,
            original_currency="INR",
        )
        url = reverse("donation-detail", args=[donation.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_patch_delete_not_allowed(self):
        donation = services.initiate_donation(
            campaign=self.live_campaign,
            donor=self.donor,
            original_amount=100,
            original_currency="INR",
        )
        url = reverse("donation-detail", args=[donation.id])

        response_put = self.client.put(url, {"original_amount": "50.00"})
        self.assertEqual(response_put.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response_patch = self.client.patch(url, {"original_amount": "50.00"})
        self.assertEqual(response_patch.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response_delete = self.client.delete(url)
        self.assertEqual(response_delete.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # --- DONATION CREATION & VALIDATION TESTS ---

    def test_successful_donation_creation(self):
        url = reverse("donation-list")
        data = {
            "campaign": str(self.live_campaign.id),
            "original_amount": "150.00",
            "original_currency": "INR",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        donation = Donation.objects.get(id=response.data["id"])
        self.assertEqual(donation.status, "pending")

    def test_invalid_amount_rejected(self):
        url = reverse("donation-list")
        data = {
            "campaign": str(self.live_campaign.id),
            "original_amount": "-50.00",
            "original_currency": "INR",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_donate_to_non_live_campaign(self):
        url = reverse("donation-list")
        data = {
            "campaign": str(self.draft_campaign.id),
            "original_amount": "100.00",
            "original_currency": "INR",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_gateway_order_id_rejected(self):
        services.create_donation(
            campaign=self.live_campaign,
            donor=self.donor,
            original_amount=100,
            original_currency="INR",
            settled_amount=100,
            settled_currency="INR",
            gateway_type="stripe",
            gateway_order_id="unique_gateway_order_id_123",
        )
        with self.assertRaises(ValueError):
            services.create_donation(
                campaign=self.live_campaign,
                donor=self.donor,
                original_amount=100,
                original_currency="INR",
                settled_amount=100,
                settled_currency="INR",
                gateway_type="stripe",
                gateway_order_id="unique_gateway_order_id_123",
            )

    def test_guest_donation_stores_donor_none(self):
        url = reverse("donation-list")
        data = {
            "campaign": str(self.live_campaign.id),
            "original_amount": "100.00",
            "original_currency": "INR",
        }
        response = self.client.post(url, data)
        donation = Donation.objects.get(id=response.data["id"])
        self.assertIsNone(donation.donor)

    def test_authenticated_donation_stores_donor_correctly(self):
        self.authenticate(self.donor)
        url = reverse("donation-list")
        data = {
            "campaign": str(self.live_campaign.id),
            "original_amount": "100.00",
            "original_currency": "INR",
        }
        response = self.client.post(url, data)
        donation = Donation.objects.get(id=response.data["id"])
        self.assertEqual(donation.donor, self.donor)

    def test_anonymous_donation_stores_is_anonymous_true(self):
        url = reverse("donation-list")
        data = {
            "campaign": str(self.live_campaign.id),
            "original_amount": "100.00",
            "original_currency": "INR",
            "is_anonymous": True,
        }
        response = self.client.post(url, data)
        donation = Donation.objects.get(id=response.data["id"])
        self.assertTrue(donation.is_anonymous)

    # --- BUSINESS LOGIC TESTS ---

    def test_successful_donation_increments_campaign_raised_amount(self):
        donation = services.initiate_donation(
            campaign=self.live_campaign,
            donor=self.donor,
            original_amount=500,
            original_currency="INR",
        )
        services.mark_donation_success(donation=donation, gateway_transaction_id="tx_123")

        self.live_campaign.refresh_from_db()
        self.assertEqual(self.live_campaign.raised_amount, 500)

    def test_failed_donation_does_not_update_campaign(self):
        donation = services.initiate_donation(
            campaign=self.live_campaign,
            donor=self.donor,
            original_amount=500,
            original_currency="INR",
        )
        services.mark_donation_failed(donation=donation)

        self.live_campaign.refresh_from_db()
        self.assertEqual(self.live_campaign.raised_amount, 0)

    def test_refund_decreases_campaign_raised_amount(self):
        donation = services.initiate_donation(
            campaign=self.live_campaign,
            donor=self.donor,
            original_amount=500,
            original_currency="INR",
        )
        services.mark_donation_success(donation=donation, gateway_transaction_id="tx_123")

        self.live_campaign.refresh_from_db()
        self.assertEqual(self.live_campaign.raised_amount, 500)

        services.refund_donation(donation=donation)
        self.live_campaign.refresh_from_db()
        self.assertEqual(self.live_campaign.raised_amount, 0)

    def test_duplicate_success_callback_is_idempotent(self):
        donation = services.initiate_donation(
            campaign=self.live_campaign,
            donor=self.donor,
            original_amount=500,
            original_currency="INR",
        )
        services.mark_donation_success(donation=donation, gateway_transaction_id="tx_123")
        # Call again
        services.mark_donation_success(donation=donation, gateway_transaction_id="tx_123")

        self.live_campaign.refresh_from_db()
        self.assertEqual(self.live_campaign.raised_amount, 500)

    def test_invalid_state_transitions_raise_errors(self):
        donation = services.initiate_donation(
            campaign=self.live_campaign,
            donor=self.donor,
            original_amount=500,
            original_currency="INR",
        )
        services.mark_donation_failed(donation=donation)

        # Cannot mark a failed donation as successful
        with self.assertRaises(ValueError):
            services.mark_donation_success(donation=donation, gateway_transaction_id="tx_123")

        # Cannot refund a pending donation
        donation2 = services.initiate_donation(
            campaign=self.live_campaign,
            donor=self.donor,
            original_amount=500,
            original_currency="INR",
        )
        with self.assertRaises(ValueError):
            services.refund_donation(donation=donation2)

    # --- SERIALIZATION TESTS ---

    def test_anonymous_donations_hide_donor_identity(self):
        donation = services.initiate_donation(
            campaign=self.live_campaign,
            donor=self.donor,
            original_amount=500,
            original_currency="INR",
            is_anonymous=True,
        )
        url = reverse("donation-detail", args=[donation.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data["donor"]["id"])
        self.assertEqual(response.data["donor"]["username"], "Anonymous Donor")

    def test_non_anonymous_donations_expose_donor_details(self):
        donation = services.initiate_donation(
            campaign=self.live_campaign,
            donor=self.donor,
            original_amount=500,
            original_currency="INR",
            is_anonymous=False,
        )
        url = reverse("donation-detail", args=[donation.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["donor"]["id"], str(self.donor.id))
        self.assertEqual(response.data["donor"]["username"], self.donor.full_name)

    def test_receipt_url_is_serialized(self):
        donation = services.initiate_donation(
            campaign=self.live_campaign,
            donor=self.donor,
            original_amount=500,
            original_currency="INR",
            is_anonymous=False,
        )
        donation.receipt_url = "https://example.com/receipt.pdf"
        donation.save(update_fields=["receipt_url"])

        url = reverse("donation-detail", args=[donation.id])
        response = self.client.get(url)
        self.assertEqual(response.data["receipt_url"], "https://example.com/receipt.pdf")

    def test_campaign_serializer_is_nested_correctly(self):
        donation = services.initiate_donation(
            campaign=self.live_campaign,
            donor=self.donor,
            original_amount=500,
            original_currency="INR",
            is_anonymous=False,
        )
        url = reverse("donation-detail", args=[donation.id])
        response = self.client.get(url)
        self.assertEqual(response.data["campaign"]["id"], str(self.live_campaign.id))
        self.assertEqual(response.data["campaign"]["title"], self.live_campaign.title)

    # --- FILTERING TESTS ---

    def test_filter_by_campaign(self):
        campaign2 = Campaign.objects.create(
            title="Second Live Campaign",
            goal_amount=20000,
            campaign_currency="INR",
            status="live",
            category=self.category,
            created_by=self.ngo,
        )
        donation1 = services.initiate_donation(
            campaign=self.live_campaign,
            donor=self.donor,
            original_amount=100,
            original_currency="INR",
        )
        donation2 = services.initiate_donation(
            campaign=campaign2,
            donor=self.donor,
            original_amount=200,
            original_currency="INR",
        )

        results = services.list_campaign_donations(campaign_id=self.live_campaign.id)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().id, donation1.id)

    def test_filter_by_donor(self):
        donor2 = make_user("donor2@example.com", "donor", "Second Donor")
        donation1 = services.initiate_donation(
            campaign=self.live_campaign,
            donor=self.donor,
            original_amount=100,
            original_currency="INR",
        )
        donation2 = services.initiate_donation(
            campaign=self.live_campaign,
            donor=donor2,
            original_amount=200,
            original_currency="INR",
        )

        results = services.list_user_donations(user_id=self.donor.id)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().id, donation1.id)

    def test_filter_by_status(self):
        donation1 = services.initiate_donation(
            campaign=self.live_campaign,
            donor=self.donor,
            original_amount=100,
            original_currency="INR",
        )
        donation2 = services.initiate_donation(
            campaign=self.live_campaign,
            donor=self.donor,
            original_amount=200,
            original_currency="INR",
        )
        services.mark_donation_success(donation=donation1, gateway_transaction_id="tx_abc")

        success_donations = Donation.objects.filter(status="success")
        self.assertEqual(success_donations.count(), 1)
        self.assertEqual(success_donations.first().id, donation1.id)
