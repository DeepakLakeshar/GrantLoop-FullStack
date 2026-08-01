import uuid
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.campaigns.models import Campaign, Category, Verification, TransparencyLog
from apps.milestones.models import Milestone
from apps.notifications.models import Notification, NotificationType
from .models import Payout, PayoutStatus
from .gateways import get_payout_gateway, StripePayoutGateway, RazorpayPayoutGateway, MockPayoutGateway
from . import services

User = get_user_model()


class PayoutTestSuite(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(email="admin@payout.org", password="password123", full_name="Admin Boss", role="admin")
        cls.ngo1 = User.objects.create_user(email="ngo1@payout.org", password="password123", full_name="NGO One", role="ngo")
        cls.ngo2 = User.objects.create_user(email="ngo2@payout.org", password="password123", full_name="NGO Two", role="ngo")
        cls.donor = User.objects.create_user(email="donor@payout.org", password="password123", full_name="Donor Dan", role="donor")

        cls.category = Category.objects.create(name="Payout Grants", slug="payout-grants")

    def create_verified_campaign(self, owner, title="Verified Campaign", goal=Decimal("50000.00"), raised=Decimal("10000.00"), c_status="live"):
        c = Campaign.objects.create(
            title=title,
            goal_amount=goal,
            raised_amount=raised,
            campaign_currency="INR",
            status=c_status,
            category=self.category,
            created_by=owner,
        )
        Verification.objects.create(campaign=c, verified_by=self.admin, status="approved", notes="Looks great!")
        return c

    def test_01_donor_has_no_access_to_payouts(self):
        self.client.force_authenticate(user=self.donor)
        url = reverse("payout-list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_02_ngo_can_create_payout_request_for_own_campaign(self):
        c = self.create_verified_campaign(owner=self.ngo1, raised=Decimal("5000.00"))
        self.client.force_authenticate(user=self.ngo1)
        url = reverse("payout-list")
        data = {"campaign": str(c.id), "requested_amount": "2000.00", "currency": "INR", "request_notes": "Urgent funds"}
        res = self.client.post(url, data=data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["status"], "pending")
        self.assertEqual(Decimal(res.data["requested_amount"]), Decimal("2000.00"))
        self.assertEqual(Decimal(res.data["available_balance_before"]), Decimal("5000.00"))
        self.assertEqual(Decimal(res.data["available_balance_after"]), Decimal("3000.00"))

    def test_03_ngo_cannot_create_payout_for_other_ngo_campaign(self):
        c = self.create_verified_campaign(owner=self.ngo1, raised=Decimal("5000.00"))
        self.client.force_authenticate(user=self.ngo2)
        url = reverse("payout-list")
        data = {"campaign": str(c.id), "requested_amount": "1000.00"}
        res = self.client.post(url, data=data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_04_ngo_cannot_call_admin_state_transition_actions(self):
        c = self.create_verified_campaign(owner=self.ngo1, raised=Decimal("5000.00"))
        payout = services.create_payout_request(campaign=c, user=self.ngo1, requested_amount=Decimal("1000.00"))
        self.client.force_authenticate(user=self.ngo1)

        for action_name in ["approve", "reject", "process", "complete", "fail"]:
            url = reverse(f"payout-{action_name}", args=[payout.id])
            res = self.client.post(url, data={})
            self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN, f"Action {action_name} failed to block NGO")

    def test_05_admin_can_approve_and_modify_amount(self):
        c = self.create_verified_campaign(owner=self.ngo1, raised=Decimal("5000.00"))
        payout = services.create_payout_request(campaign=c, user=self.ngo1, requested_amount=Decimal("2000.00"))
        self.client.force_authenticate(user=self.admin)
        url = reverse("payout-approve", args=[payout.id])
        res = self.client.post(url, data={"approved_amount": "1800.00", "admin_notes": "Approved with deduction"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["status"], "approved")
        self.assertEqual(Decimal(res.data["approved_amount"]), Decimal("1800.00"))
        self.assertEqual(Decimal(res.data["available_balance_after"]), Decimal("3200.00"))

    def test_06_reject_payout_request_releases_balance(self):
        c = self.create_verified_campaign(owner=self.ngo1, raised=Decimal("5000.00"))
        payout = services.create_payout_request(campaign=c, user=self.ngo1, requested_amount=Decimal("5000.00"))
        self.assertEqual(services.get_available_balance(c), Decimal("0.00"))

        self.client.force_authenticate(user=self.admin)
        url = reverse("payout-reject", args=[payout.id])
        res = self.client.post(url, data={"rejection_reason": "Missing receipt documents"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["status"], "rejected")
        self.assertEqual(services.get_available_balance(c), Decimal("5000.00"))

    def test_07_validation_rejects_zero_or_negative_amount(self):
        c = self.create_verified_campaign(owner=self.ngo1, raised=Decimal("5000.00"))
        with self.assertRaises(ValueError):
            services.create_payout_request(campaign=c, user=self.ngo1, requested_amount=Decimal("0.00"))
        with self.assertRaises(ValueError):
            services.create_payout_request(campaign=c, user=self.ngo1, requested_amount=Decimal("-10.00"))

    def test_08_validation_rejects_inactive_campaign(self):
        for status_val in ["draft", "pending_verification", "rejected", "archived"]:
            c = self.create_verified_campaign(owner=self.ngo1, raised=Decimal("5000.00"), c_status=status_val)
            with self.assertRaises(ValueError):
                services.create_payout_request(campaign=c, user=self.ngo1, requested_amount=Decimal("100.00"))

    def test_09_validation_rejects_unverified_campaign(self):
        c = Campaign.objects.create(title="Unverified", goal_amount=Decimal("1000.00"), raised_amount=Decimal("500.00"), status="live", created_by=self.ngo1)
        with self.assertRaises(ValueError):
            services.create_payout_request(campaign=c, user=self.ngo1, requested_amount=Decimal("100.00"))

    def test_10_validation_rejects_exceeding_available_balance(self):
        c = self.create_verified_campaign(owner=self.ngo1, raised=Decimal("1000.00"))
        with self.assertRaises(ValueError):
            services.create_payout_request(campaign=c, user=self.ngo1, requested_amount=Decimal("1000.01"))

    def test_11_validation_rejects_when_pending_payout_already_exists(self):
        c = self.create_verified_campaign(owner=self.ngo1, raised=Decimal("5000.00"))
        services.create_payout_request(campaign=c, user=self.ngo1, requested_amount=Decimal("1000.00"))
        with self.assertRaises(ValueError):
            services.create_payout_request(campaign=c, user=self.ngo1, requested_amount=Decimal("500.00"))

    def test_12_validation_rejects_when_required_milestones_incomplete(self):
        c = self.create_verified_campaign(owner=self.ngo1, raised=Decimal("5000.00"))
        m = Milestone.objects.create(campaign=c, title="Phase 1", target_amount=Decimal("2000.00"), status="in_progress")
        with self.assertRaises(ValueError):
            services.create_payout_request(campaign=c, user=self.ngo1, requested_amount=Decimal("1000.00"))

        m.status = "completed"
        m.save()
        # Should now succeed
        p = services.create_payout_request(campaign=c, user=self.ngo1, requested_amount=Decimal("1000.00"))
        self.assertIsNotNone(p.id)

    def test_13_gateway_abstraction_providers(self):
        for gw_type, expected_cls in [("stripe", StripePayoutGateway), ("razorpay", RazorpayPayoutGateway), ("mock", MockPayoutGateway)]:
            gw = get_payout_gateway(gw_type)
            self.assertIsInstance(gw, expected_cls)
            res = gw.initiate_transfer(account_reference="test_acc", amount=Decimal("500.00"), currency="INR")
            self.assertTrue(res.success)
            self.assertEqual(res.status, "processing")

    def test_14_process_payout_via_gateway(self):
        c = self.create_verified_campaign(owner=self.ngo1, raised=Decimal("5000.00"))
        p = services.create_payout_request(campaign=c, user=self.ngo1, requested_amount=Decimal("1000.00"))
        p = services.approve_payout(payout_id=p.id, admin_user=self.admin)
        self.client.force_authenticate(user=self.admin)
        url = reverse("payout-process", args=[p.id])
        res = self.client.post(url, data={"gateway_type": "stripe", "account_reference": "acct_dev_123"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["status"], "processing")
        self.assertTrue(res.data["gateway_reference"].startswith("tr_stripe_") or res.data["gateway_reference"].startswith("pay_"))

    def test_15_complete_payout_and_transparency_log(self):
        c = self.create_verified_campaign(owner=self.ngo1, raised=Decimal("5000.00"))
        p = services.create_payout_request(campaign=c, user=self.ngo1, requested_amount=Decimal("2000.00"))
        p = services.approve_payout(payout_id=p.id, admin_user=self.admin)
        p = services.mark_processing(payout_id=p.id, admin_user=self.admin, gateway_type="razorpay")

        self.client.force_authenticate(user=self.admin)
        url = reverse("payout-complete", args=[p.id])
        res = self.client.post(url, data={"transfer_reference": "settled_utr_001"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["status"], "completed")
        self.assertEqual(res.data["transfer_reference"], "settled_utr_001")
        self.assertTrue(TransparencyLog.objects.filter(campaign=c, action__icontains="Fund disbursement of 2000.00 INR completed").exists())

    def test_16_fail_payout_releases_reserved_funds(self):
        c = self.create_verified_campaign(owner=self.ngo1, raised=Decimal("3000.00"))
        p = services.create_payout_request(campaign=c, user=self.ngo1, requested_amount=Decimal("2500.00"))
        p = services.approve_payout(payout_id=p.id, admin_user=self.admin)
        p = services.mark_processing(payout_id=p.id, admin_user=self.admin)
        self.assertEqual(services.get_available_balance(c), Decimal("500.00"))

        p = services.mark_failed(payout_id=p.id, admin_user=self.admin, failure_reason="Invalid routing number")
        self.assertEqual(p.status, "failed")
        self.assertEqual(services.get_available_balance(c), Decimal("3000.00"))

    def test_17_cancel_payout_only_while_pending_and_soft_delete(self):
        c = self.create_verified_campaign(owner=self.ngo1, raised=Decimal("5000.00"))
        p = services.create_payout_request(campaign=c, user=self.ngo1, requested_amount=Decimal("1000.00"))

        self.client.force_authenticate(user=self.ngo1)
        url = reverse("payout-detail", args=[p.id])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        p_refresh = Payout.objects.all_with_deleted().get(id=p.id)
        self.assertEqual(p_refresh.status, "cancelled")
        self.assertTrue(p_refresh.is_deleted)

        # Cannot cancel if approved
        p2 = services.create_payout_request(campaign=c, user=self.ngo1, requested_amount=Decimal("1000.00"))
        p2 = services.approve_payout(payout_id=p2.id, admin_user=self.admin)
        url2 = reverse("payout-detail", args=[p2.id])
        res2 = self.client.delete(url2)
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_18_notifications_dispatched_at_all_stages(self):
        c = self.create_verified_campaign(owner=self.ngo1, raised=Decimal("10000.00"))
        # Requested
        p = services.create_payout_request(campaign=c, user=self.ngo1, requested_amount=Decimal("1000.00"))
        self.assertTrue(Notification.objects.filter(recipient=self.ngo1, notification_type=NotificationType.PAYOUT_REQUESTED).exists())
        self.assertTrue(Notification.objects.filter(recipient=self.admin, notification_type=NotificationType.PAYOUT_REQUESTED).exists())

        # Approved
        p = services.approve_payout(payout_id=p.id, admin_user=self.admin)
        self.assertTrue(Notification.objects.filter(recipient=self.ngo1, notification_type=NotificationType.PAYOUT_APPROVED).exists())

        # Processing
        p = services.mark_processing(payout_id=p.id, admin_user=self.admin)
        self.assertTrue(Notification.objects.filter(recipient=self.ngo1, notification_type=NotificationType.PAYOUT_PROCESSING).exists())

        # Completed
        p = services.mark_completed(payout_id=p.id, admin_user=self.admin)
        self.assertTrue(Notification.objects.filter(recipient=self.ngo1, notification_type=NotificationType.PAYOUT_COMPLETED).exists())

        # Cancelled testing on another request
        p2 = services.create_payout_request(campaign=c, user=self.ngo1, requested_amount=Decimal("500.00"))
        p2 = services.cancel_payout(payout_id=p2.id, user=self.ngo1)
        self.assertTrue(Notification.objects.filter(recipient=self.ngo1, notification_type=NotificationType.PAYOUT_CANCELLED).exists())

    def test_19_repeated_approve_process_complete_requests_idempotence(self):
        c = self.create_verified_campaign(owner=self.ngo1, raised=Decimal("10000.00"))
        p = services.create_payout_request(campaign=c, user=self.ngo1, requested_amount=Decimal("2000.00"))

        # Repeated approve
        p_app1 = services.approve_payout(payout_id=p.id, admin_user=self.admin)
        p_app2 = services.approve_payout(payout_id=p.id, admin_user=self.admin)
        self.assertEqual(p_app1.updated_at, p_app2.updated_at)

        # Repeated process
        p_proc1 = services.mark_processing(payout_id=p.id, admin_user=self.admin)
        p_proc2 = services.mark_processing(payout_id=p.id, admin_user=self.admin)
        self.assertEqual(p_proc1.gateway_reference, p_proc2.gateway_reference)

        # Repeated complete
        p_comp1 = services.mark_completed(payout_id=p.id, admin_user=self.admin, transfer_reference="utr_fixed_123")
        p_comp2 = services.mark_completed(payout_id=p.id, admin_user=self.admin, transfer_reference="utr_fixed_999")
        self.assertEqual(p_comp2.transfer_reference, "utr_fixed_123")  # Idempotently preserved first settlement reference

    def test_20_duplicate_gateway_callbacks_idempotent_handling(self):
        c = self.create_verified_campaign(owner=self.ngo1, raised=Decimal("5000.00"))
        p = services.create_payout_request(campaign=c, user=self.ngo1, requested_amount=Decimal("1000.00"))
        p = services.approve_payout(payout_id=p.id, admin_user=self.admin)
        p = services.mark_processing(payout_id=p.id, admin_user=self.admin)
        
        # Initial callback confirms completion
        services.mark_completed(payout_id=p.id, admin_user=self.admin, transfer_reference="cb_ref_001")
        log_count = TransparencyLog.objects.filter(campaign=c, action__icontains="Fund disbursement").count()

        # Second identical callback should not create duplicate log entries
        services.mark_completed(payout_id=p.id, admin_user=self.admin, transfer_reference="cb_ref_001")
        self.assertEqual(TransparencyLog.objects.filter(campaign=c, action__icontains="Fund disbursement").count(), log_count)

    def test_21_concurrent_payout_reservation_prevention(self):
        """
        Ensures that once a pending payout reserves available balance,
        any concurrent attempt to draw against the same unreserved pool fails.
        """
        c = self.create_verified_campaign(owner=self.ngo1, raised=Decimal("5000.00"))
        p1 = services.create_payout_request(campaign=c, user=self.ngo1, requested_amount=Decimal("4000.00"))
        self.assertEqual(services.get_available_balance(c), Decimal("1000.00"))

        with self.assertRaises(ValueError) as ctx:
            # Note: since p1 is pending, creating another pending request for same campaign is blocked by dual invariant!
            # Let's approve p1 so we can test the financial balance constraint specifically!
            services.approve_payout(payout_id=p1.id, admin_user=self.admin)
            services.create_payout_request(campaign=c, user=self.ngo1, requested_amount=Decimal("1500.00"))
        self.assertIn("exceeds available", str(ctx.exception))

    def test_22_concurrent_approve_vs_cancel_race(self):
        """
        Verifies that once a payout transitions out of pending via approval or cancellation,
        any racing conflicting transition is rejected.
        """
        c = self.create_verified_campaign(owner=self.ngo1, raised=Decimal("5000.00"))
        p = services.create_payout_request(campaign=c, user=self.ngo1, requested_amount=Decimal("1000.00"))

        # Assume cancellation wins race
        services.cancel_payout(payout_id=p.id, user=self.ngo1)
        with self.assertRaises(ValueError):
            # Admin approval arrives late and is rejected
            services.approve_payout(payout_id=p.id, admin_user=self.admin)

    def test_23_audit_balance_tracking_precision(self):
        c = self.create_verified_campaign(owner=self.ngo1, raised=Decimal("12345.67"))
        p = services.create_payout_request(campaign=c, user=self.ngo1, requested_amount=Decimal("2345.67"))
        self.assertEqual(p.available_balance_before, Decimal("12345.67"))
        self.assertEqual(p.available_balance_after, Decimal("10000.00"))

        # Admin approves with lower amount (e.g. fee holdback)
        p_app = services.approve_payout(payout_id=p.id, admin_user=self.admin, approved_amount=Decimal("2000.00"))
        self.assertEqual(p_app.available_balance_before, Decimal("12345.67"))
        self.assertEqual(p_app.available_balance_after, Decimal("10345.67"))

    def test_24_list_endpoints_scoping(self):
        c1 = self.create_verified_campaign(owner=self.ngo1, title="C1", raised=Decimal("5000.00"))
        c2 = self.create_verified_campaign(owner=self.ngo2, title="C2", raised=Decimal("5000.00"))
        p1 = services.create_payout_request(campaign=c1, user=self.ngo1, requested_amount=Decimal("100.00"))
        p2 = services.create_payout_request(campaign=c2, user=self.ngo2, requested_amount=Decimal("200.00"))

        self.client.force_authenticate(user=self.ngo1)
        res_ngo = self.client.get(reverse("payout-list"))
        self.assertEqual(len(res_ngo.data), 1)
        self.assertEqual(res_ngo.data[0]["id"], str(p1.id))

        self.client.force_authenticate(user=self.admin)
        res_admin = self.client.get(reverse("payout-list"))
        self.assertEqual(len(res_admin.data), 2)

    def test_25_retrieve_unauthorized_existing_payout_returns_403_not_404(self):
        c2 = self.create_verified_campaign(owner=self.ngo2, title="C2", raised=Decimal("5000.00"))
        p2 = services.create_payout_request(campaign=c2, user=self.ngo2, requested_amount=Decimal("200.00"))

        self.client.force_authenticate(user=self.ngo1)
        url = reverse("payout-detail", args=[p2.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_26_api_search_and_filter_support(self):
        c = self.create_verified_campaign(owner=self.ngo1, title="Special Health Drive", raised=Decimal("10000.00"))
        p1 = services.create_payout_request(campaign=c, user=self.ngo1, requested_amount=Decimal("1000.00"), request_notes="Urgent medical supplies")
        p2 = services.create_payout_request(campaign=self.create_verified_campaign(owner=self.ngo2, title="Education Fund", raised=Decimal("5000.00")), user=self.ngo2, requested_amount=Decimal("2000.00"), request_notes="Books acquisition")

        self.client.force_authenticate(user=self.admin)
        res_search = self.client.get(reverse("payout-list"), {"search": "medical"})
        self.assertEqual(len(res_search.data), 1)
        self.assertEqual(res_search.data[0]["id"], str(p1.id))

        res_filter = self.client.get(reverse("payout-list"), {"status": "pending"})
        self.assertEqual(len(res_filter.data), 2)

    def test_27_unauthenticated_requests_blocked(self):
        res = self.client.get(reverse("payout-list"))
        self.assertIn(res.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_28_invalid_state_transitions_rejected(self):
        c = self.create_verified_campaign(owner=self.ngo1, raised=Decimal("5000.00"))
        p = services.create_payout_request(campaign=c, user=self.ngo1, requested_amount=Decimal("1000.00"))
        
        # Cannot process pending directly without approval
        with self.assertRaises(ValueError):
            services.mark_processing(payout_id=p.id, admin_user=self.admin)
        
        # Cannot complete pending directly
        with self.assertRaises(ValueError):
            services.mark_completed(payout_id=p.id, admin_user=self.admin)

        # Reject it
        p = services.reject_payout(payout_id=p.id, admin_user=self.admin)
        # Cannot approve rejected
        with self.assertRaises(ValueError):
            services.approve_payout(payout_id=p.id, admin_user=self.admin)

    def test_29_completed_campaign_allows_payouts_for_remaining_balance(self):
        c = self.create_verified_campaign(owner=self.ngo1, raised=Decimal("8000.00"), c_status="completed")
        p = services.create_payout_request(campaign=c, user=self.ngo1, requested_amount=Decimal("8000.00"))
        self.assertEqual(p.status, "pending")
        self.assertEqual(p.available_balance_after, Decimal("0.00"))

    def test_30_admin_can_view_cancelled_soft_deleted_in_detail(self):
        c = self.create_verified_campaign(owner=self.ngo1, raised=Decimal("5000.00"))
        p = services.create_payout_request(campaign=c, user=self.ngo1, requested_amount=Decimal("1000.00"))
        services.cancel_payout(payout_id=p.id, user=self.ngo1)

        self.client.force_authenticate(user=self.admin)
        url = reverse("payout-detail", args=[p.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["status"], "cancelled")
        self.assertTrue(res.data["is_deleted"])
