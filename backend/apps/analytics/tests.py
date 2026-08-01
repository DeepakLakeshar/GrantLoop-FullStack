import uuid
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.campaigns.models import Campaign, Category, Verification
from apps.donations.models import Donation
from apps.beneficiaries.models import Beneficiary, VerificationStatus as BenStatus
from apps.payouts.models import Payout
from apps.milestones.models import Milestone

User = get_user_model()


class AnalyticsTestSuite(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(
            email="admin@analytics.org", password="password123", full_name="Admin Chief", role="admin"
        )
        cls.ngo1 = User.objects.create_user(
            email="ngo1@analytics.org", password="password123", full_name="Health NGO", role="ngo", email_verified=True
        )
        cls.ngo2 = User.objects.create_user(
            email="ngo2@analytics.org", password="password123", full_name="Edu NGO", role="ngo", email_verified=False
        )
        cls.donor1 = User.objects.create_user(
            email="donor1@analytics.org", password="password123", full_name="Donor One", role="donor"
        )
        cls.donor2 = User.objects.create_user(
            email="donor2@analytics.org", password="password123", full_name="Donor Two", role="donor"
        )

        cls.category = Category.objects.create(name="Analytics Grants", slug="analytics-grants")

        # Create verified campaign for ngo1
        cls.camp_live = Campaign.objects.create(
            title="Hospital Construction",
            goal_amount=Decimal("100000.00"),
            raised_amount=Decimal("25000.00"),
            campaign_currency="USD",
            status="live",
            category=cls.category,
            created_by=cls.ngo1,
        )
        Verification.objects.create(campaign=cls.camp_live, verified_by=cls.admin, status="approved", notes="Approved!")

        # Create completed campaign for ngo2
        cls.camp_comp = Campaign.objects.create(
            title="School Supplies",
            goal_amount=Decimal("10000.00"),
            raised_amount=Decimal("10000.00"),
            campaign_currency="USD",
            status="completed",
            category=cls.category,
            created_by=cls.ngo2,
        )

    def create_donation_helper(self, donor, campaign, amount=Decimal("100.00"), d_status="success"):
        return Donation.objects.create(
            donor=donor,
            campaign=campaign,
            original_amount=amount,
            original_currency="USD",
            settled_amount=amount,
            settled_currency="USD",
            status=d_status,
            gateway_order_id=f"ord_{uuid.uuid4().hex[:16]}",
        )

    def create_payout_helper(self, campaign, ngo, requested=Decimal("1000.00"), approved=None, p_status="pending"):
        return Payout.objects.create(
            campaign=campaign,
            ngo=ngo,
            requested_by=ngo,
            requested_amount=requested,
            approved_amount=approved if approved is not None else requested,
            currency="USD",
            status=p_status,
            available_balance_before=Decimal("10000.00"),
            available_balance_after=Decimal("9000.00"),
        )

    # --- Role Isolation & Permission Tests ---

    def test_01_admin_dashboard_requires_authentication(self):
        res = self.client.get(reverse("analytics-admin-dashboard"))
        self.assertIn(res.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_02_admin_dashboard_role_isolation_blocks_ngo(self):
        self.client.force_authenticate(user=self.ngo1)
        res = self.client.get(reverse("analytics-admin-dashboard"))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_03_admin_dashboard_role_isolation_blocks_donor(self):
        self.client.force_authenticate(user=self.donor1)
        res = self.client.get(reverse("analytics-admin-dashboard"))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_04_admin_dashboard_success_and_metrics(self):
        self.client.force_authenticate(user=self.admin)
        res = self.client.get(reverse("analytics-admin-dashboard"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.data
        self.assertIn("total_users", data)
        self.assertIn("platform_balance", data)
        self.assertIn("recent_campaigns", data)
        self.assertGreaterEqual(data["total_users"], 5)

    def test_05_admin_dashboard_accurate_user_and_ngo_counts(self):
        self.client.force_authenticate(user=self.admin)
        res = self.client.get(reverse("analytics-admin-dashboard"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.data
        self.assertEqual(data["total_ngos"], 2)
        self.assertEqual(data["verified_ngos"], 1)
        self.assertEqual(data["pending_ngo_verifications"], 1)

    def test_06_admin_dashboard_accurate_campaign_counts_by_status(self):
        Campaign.objects.create(title="Draft C", goal_amount=Decimal("100.00"), status="draft", created_by=self.ngo1)
        Campaign.objects.create(title="Pending C", goal_amount=Decimal("100.00"), status="pending_verification", created_by=self.ngo1)
        Campaign.objects.create(title="Rejected C", goal_amount=Decimal("100.00"), status="rejected", created_by=self.ngo1)

        self.client.force_authenticate(user=self.admin)
        res = self.client.get(reverse("analytics-admin-dashboard"))
        data = res.data
        self.assertGreaterEqual(data["total_campaigns"], 5)
        self.assertGreaterEqual(data["draft_campaigns"], 1)
        self.assertGreaterEqual(data["pending_campaigns"], 1)
        self.assertGreaterEqual(data["rejected_campaigns"], 1)

    def test_07_admin_dashboard_accurate_donation_aggregations(self):
        self.create_donation_helper(self.donor1, self.camp_live, Decimal("1000.00"), "success")
        self.create_donation_helper(self.donor2, self.camp_live, Decimal("5000.00"), "success")
        self.create_donation_helper(self.donor1, self.camp_live, Decimal("200.00"), "pending")

        self.client.force_authenticate(user=self.admin)
        res = self.client.get(reverse("analytics-admin-dashboard"))
        data = res.data
        self.assertEqual(Decimal(data["total_donation_amount"]), Decimal("6000.00"))
        self.assertEqual(Decimal(data["average_donation"]), Decimal("3000.00"))
        self.assertEqual(Decimal(data["largest_donation"]), Decimal("5000.00"))
        self.assertGreaterEqual(data["successful_donations"], 2)
        self.assertGreaterEqual(data["pending_donations"], 1)

    def test_08_admin_dashboard_accurate_beneficiary_counts_by_status(self):
        Beneficiary.objects.create(campaign=self.camp_live, full_name="Ben One", verification_status=BenStatus.VERIFIED)
        Beneficiary.objects.create(campaign=self.camp_live, full_name="Ben Two", verification_status=BenStatus.PENDING)

        self.client.force_authenticate(user=self.admin)
        res = self.client.get(reverse("analytics-admin-dashboard"))
        data = res.data
        self.assertGreaterEqual(data["total_beneficiaries"], 2)
        self.assertGreaterEqual(data["verified_beneficiaries"], 1)
        self.assertGreaterEqual(data["pending_beneficiaries"], 1)

    def test_09_admin_dashboard_accurate_payout_counts_and_amounts(self):
        self.create_payout_helper(self.camp_live, self.ngo1, Decimal("2000.00"), Decimal("2000.00"), "completed")
        self.create_payout_helper(self.camp_live, self.ngo1, Decimal("1000.00"), None, "pending")

        self.client.force_authenticate(user=self.admin)
        res = self.client.get(reverse("analytics-admin-dashboard"))
        data = res.data
        self.assertGreaterEqual(data["completed_payouts"], 1)
        self.assertGreaterEqual(data["pending_payouts"], 1)
        self.assertGreaterEqual(Decimal(data["total_paid_amount"]), Decimal("2000.00"))

    def test_10_admin_dashboard_recent_activities_limited_to_5(self):
        for i in range(8):
            self.create_donation_helper(self.donor1, self.camp_live, Decimal("10.00"), "success")
        self.client.force_authenticate(user=self.admin)
        res = self.client.get(reverse("analytics-admin-dashboard"))
        self.assertEqual(len(res.data["recent_donations"]), 5)

    def test_11_ngo_dashboard_requires_authentication(self):
        res = self.client.get(reverse("analytics-ngo-dashboard"))
        self.assertIn(res.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_12_ngo_dashboard_role_isolation_blocks_admin(self):
        self.client.force_authenticate(user=self.admin)
        res = self.client.get(reverse("analytics-ngo-dashboard"))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_13_ngo_dashboard_role_isolation_blocks_donor(self):
        self.client.force_authenticate(user=self.donor1)
        res = self.client.get(reverse("analytics-ngo-dashboard"))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_14_ngo_dashboard_success_and_scoping(self):
        self.client.force_authenticate(user=self.ngo1)
        res = self.client.get(reverse("analytics-ngo-dashboard"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.data
        self.assertIn("my_campaigns", data)
        self.assertIn("available_balance", data)
        self.assertEqual(data["my_campaigns"], 1)

    def test_15_ngo_dashboard_computes_funding_percentage(self):
        self.client.force_authenticate(user=self.ngo1)
        res = self.client.get(reverse("analytics-ngo-dashboard"))
        # camp_live has goal 100000, raised 25000 -> 25.0%
        self.assertEqual(res.data["funding_percentage"], 25.0)

    def test_16_ngo_dashboard_computes_milestones_and_completion_percentage(self):
        Milestone.objects.create(campaign=self.camp_live, title="M1", target_amount=Decimal("1000.00"), status="completed")
        Milestone.objects.create(campaign=self.camp_live, title="M2", target_amount=Decimal("1000.00"), status="pending")
        self.client.force_authenticate(user=self.ngo1)
        res = self.client.get(reverse("analytics-ngo-dashboard"))
        self.assertEqual(res.data["milestones"], 2)
        self.assertEqual(res.data["completed_milestones"], 1)
        self.assertEqual(res.data["completion_percentage"], 50.0)

    def test_17_ngo_dashboard_reports_available_balance(self):
        self.client.force_authenticate(user=self.ngo1)
        res = self.client.get(reverse("analytics-ngo-dashboard"))
        # raised is 25000, no reserved payouts yet
        self.assertEqual(Decimal(res.data["available_balance"]), Decimal("25000.00"))

    def test_18_donor_dashboard_requires_authentication(self):
        res = self.client.get(reverse("analytics-donor-dashboard"))
        self.assertIn(res.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_19_donor_dashboard_role_isolation_blocks_admin_and_ngo(self):
        self.client.force_authenticate(user=self.admin)
        res = self.client.get(reverse("analytics-donor-dashboard"))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.ngo1)
        res = self.client.get(reverse("analytics-donor-dashboard"))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_20_donor_dashboard_scopes_donations_to_contributor(self):
        self.create_donation_helper(self.donor1, self.camp_live, Decimal("100.00"), "success")
        self.create_donation_helper(self.donor2, self.camp_live, Decimal("999.00"), "success")
        self.client.force_authenticate(user=self.donor1)
        res = self.client.get(reverse("analytics-donor-dashboard"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(res.data["total_amount_donated"]), Decimal("100.00"))

    def test_21_donor_dashboard_computes_total_average_largest_donations(self):
        self.create_donation_helper(self.donor1, self.camp_live, Decimal("300.00"), "success")
        self.create_donation_helper(self.donor1, self.camp_live, Decimal("700.00"), "success")

        self.client.force_authenticate(user=self.donor1)
        res = self.client.get(reverse("analytics-donor-dashboard"))
        self.assertEqual(Decimal(res.data["total_amount_donated"]), Decimal("1000.00"))
        self.assertEqual(Decimal(res.data["average_donation"]), Decimal("500.00"))
        self.assertEqual(Decimal(res.data["largest_donation"]), Decimal("700.00"))
        self.assertEqual(res.data["campaigns_supported"], 1)

    def test_22_chart_donations_returns_12_month_array(self):
        self.client.force_authenticate(user=self.admin)
        res = self.client.get(reverse("analytics-charts", args=["donations"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 12)
        self.assertEqual(res.data[0]["month"], "Jan")
        self.assertEqual(res.data[11]["month"], "Dec")

    def test_23_chart_payouts_returns_12_month_array(self):
        self.client.force_authenticate(user=self.ngo1)
        res = self.client.get(reverse("analytics-charts", args=["payouts"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 12)

    def test_24_chart_campaigns_returns_12_month_array(self):
        self.client.force_authenticate(user=self.admin)
        res = self.client.get(reverse("analytics-charts", args=["campaigns"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 12)
        # We have at least 2 campaigns in current month
        total_chart_vals = sum(item["value"] for item in res.data)
        self.assertGreaterEqual(total_chart_vals, 2.0)

    def test_25_chart_users_returns_12_month_array(self):
        self.client.force_authenticate(user=self.admin)
        res = self.client.get(reverse("analytics-charts", args=["users"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 12)
        total_chart_vals = sum(item["value"] for item in res.data)
        self.assertGreaterEqual(total_chart_vals, 5.0)

    def test_26_chart_endpoint_rejects_invalid_chart_type(self):
        self.client.force_authenticate(user=self.admin)
        res = self.client.get(reverse("analytics-charts", args=["invalid_chart"]))
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_27_leaderboards_top_campaigns_ordered_by_raised_amount(self):
        self.client.force_authenticate(user=self.admin)
        res = self.client.get(reverse("analytics-leaderboards", args=["top-campaigns"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.data), 2)
        # camp_live has 25000, camp_comp has 10000 -> camp_live should rank #1
        self.assertEqual(res.data[0]["name"], self.camp_live.title)

    def test_28_leaderboards_top_ngos_ordered_by_total_raised(self):
        self.client.force_authenticate(user=self.admin)
        res = self.client.get(reverse("analytics-leaderboards", args=["top-ngos"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.data), 2)
        self.assertEqual(res.data[0]["name"], self.ngo1.full_name or self.ngo1.email)

    def test_29_leaderboards_top_donors_ordered_by_total_donated(self):
        self.create_donation_helper(self.donor1, self.camp_live, Decimal("5000.00"), "success")
        self.create_donation_helper(self.donor2, self.camp_live, Decimal("100.00"), "success")

        self.client.force_authenticate(user=self.admin)
        res = self.client.get(reverse("analytics-leaderboards", args=["top-donors"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]["name"], self.donor1.full_name)

    def test_30_leaderboards_most_active_campaigns_ordered_by_donation_count(self):
        for i in range(3):
            self.create_donation_helper(self.donor1, self.camp_comp, Decimal("10.00"), "success")

        self.client.force_authenticate(user=self.admin)
        res = self.client.get(reverse("analytics-leaderboards", args=["most-active-campaigns"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # camp_comp has 3 donations now -> should rank highest in activity count
        self.assertEqual(res.data[0]["name"], self.camp_comp.title)

    def test_31_leaderboards_largest_donations(self):
        self.create_donation_helper(self.donor1, self.camp_live, Decimal("8888.00"), "success")
        self.client.force_authenticate(user=self.admin)
        res = self.client.get(reverse("analytics-leaderboards", args=["largest-donations"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(res.data[0]["amount"]), Decimal("8888.00"))

    def test_32_leaderboards_largest_payouts(self):
        self.create_payout_helper(self.camp_live, self.ngo1, Decimal("9500.00"), Decimal("9500.00"), "completed")
        self.client.force_authenticate(user=self.admin)
        res = self.client.get(reverse("analytics-leaderboards", args=["largest-payouts"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(res.data[0]["amount"]), Decimal("9500.00"))

    def test_33_leaderboards_rejects_invalid_type(self):
        self.client.force_authenticate(user=self.admin)
        res = self.client.get(reverse("analytics-leaderboards", args=["invalid-type"]))
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_34_analytics_filtering_by_status_and_year(self):
        self.client.force_authenticate(user=self.admin)
        res_live = self.client.get(reverse("analytics-admin-dashboard"), {"status": "live"})
        self.assertEqual(res_live.status_code, status.HTTP_200_OK)

        res_year = self.client.get(reverse("analytics-admin-dashboard"), {"year": "2026"})
        self.assertEqual(res_year.status_code, status.HTTP_200_OK)

    def test_35_analytics_searching_by_campaign_title(self):
        self.client.force_authenticate(user=self.admin)
        res_search = self.client.get(reverse("analytics-admin-dashboard"), {"search": "Hospital"})
        self.assertEqual(res_search.status_code, status.HTTP_200_OK)

    def test_36_empty_dataset_edge_case_handling(self):
        # Fresh user with zero activity should return zeroed stats without errors
        new_donor = User.objects.create_user(email="empty@donor.org", password="pass", role="donor")
        self.client.force_authenticate(user=new_donor)
        res = self.client.get(reverse("analytics-donor-dashboard"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["total_donations"], 0)
        self.assertEqual(Decimal(res.data["total_amount_donated"]), Decimal("0.00"))
