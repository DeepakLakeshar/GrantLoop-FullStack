from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.campaigns.models import Campaign
from apps.beneficiaries.models import Beneficiary
from apps.documents.models import Document

User = get_user_model()


def make_user(email, role, full_name="Test User"):
    return User.objects.create_user(email=email, password="correcthorse8", role=role, full_name=full_name)


def fake_file(name="evidence.jpg"):
    return SimpleUploadedFile(name, b"fake-file-bytes", content_type="image/jpeg")


class DocumentUploadTests(APITestCase):
    def setUp(self):
        self.ngo = make_user("ngo@example.com", "ngo", "WaterHelp")
        self.other_ngo = make_user("other@example.com", "ngo", "Other NGO")
        self.institution = make_user("inst@example.com", "institution", "Global Trust")
        self.donor = make_user("donor@example.com", "donor", "Sarah Chen")
        self.campaign = Campaign.objects.create(created_by=self.ngo, title="Water Project", goal_amount=1000, status="live")

    def authenticate(self, user):
        response = self.client.post(reverse("auth-login"), {"email": user.email, "password": "correcthorse8"})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def test_owning_ngo_can_upload_campaign_document(self):
        self.authenticate(self.ngo)
        response = self.client.post(reverse("document-list"), {
            "campaign": str(self.campaign.id), "document_type": "photo", "file": fake_file(),
        }, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertIsNotNone(response.data["file_url"])
        self.assertEqual(response.data["status"], "pending")

    def test_other_ngo_cannot_upload_to_foreign_campaign(self):
        self.authenticate(self.other_ngo)
        response = self.client.post(reverse("document-list"), {
            "campaign": str(self.campaign.id), "document_type": "photo", "file": fake_file(),
        }, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_institution_can_upload_to_any_campaign(self):
        self.authenticate(self.institution)
        response = self.client.post(reverse("document-list"), {
            "campaign": str(self.campaign.id), "document_type": "inspection_report", "file": fake_file(),
        }, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_donor_cannot_upload_document(self):
        self.authenticate(self.donor)
        response = self.client.post(reverse("document-list"), {
            "campaign": str(self.campaign.id), "document_type": "photo", "file": fake_file(),
        }, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_cannot_upload_at_all(self):
        response = self.client.post(reverse("document-list"), {
            "campaign": str(self.campaign.id), "document_type": "photo", "file": fake_file(),
        }, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_zero_scopes_set_rejected(self):
        self.authenticate(self.ngo)
        response = self.client.post(reverse("document-list"), {
            "document_type": "photo", "file": fake_file(),
        }, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_two_scopes_set_rejected(self):
        beneficiary = Beneficiary.objects.create(
            campaign=self.campaign,
            full_name="Some Beneficiary",
            email="some@example.com",
            phone_number="+15555555555",
            address="123 Street",
            city="City",
            state="State",
            country="US",
            postal_code="12345",
            government_id="GOV_SOME",
        )
        self.authenticate(self.ngo)
        response = self.client.post(reverse("document-list"), {
            "campaign": str(self.campaign.id), "beneficiary": str(beneficiary.id),
            "document_type": "photo", "file": fake_file(),
        }, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DocumentPrivacyTests(APITestCase):
    def setUp(self):
        self.ngo = make_user("ngo2@example.com", "ngo", "NGO Two")
        self.donor = make_user("donor2@example.com", "donor", "Donor Two")
        self.institution = make_user("inst2@example.com", "institution", "Institution Two")
        self.campaign = Campaign.objects.create(created_by=self.ngo, title="Privacy Test", goal_amount=1000, status="live")
        self.beneficiary = Beneficiary.objects.create(
            campaign=self.campaign,
            full_name="Private Beneficiary",
            email="private@example.com",
            phone_number="+15555555555",
            address="123 Street",
            city="City",
            state="State",
            country="US",
            postal_code="12345",
            government_id="GOV_PRIV",
        )

    def authenticate(self, user):
        response = self.client.post(reverse("auth-login"), {"email": user.email, "password": "correcthorse8"})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def test_documents_require_authentication_even_to_list(self):
        response = self.client.get(reverse("document-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_donor_cannot_see_beneficiary_scoped_document(self):
        Document.objects.create(
            beneficiary=self.beneficiary, document_type="government_id",
            file=fake_file(), uploaded_by=self.ngo,
        )
        self.authenticate(self.donor)
        response = self.client.get(reverse("document-list"))
        self.assertEqual(len(response.data["results"] if "results" in response.data else response.data), 0)

    def test_institution_can_see_beneficiary_scoped_document(self):
        Document.objects.create(
            beneficiary=self.beneficiary, document_type="government_id",
            file=fake_file(), uploaded_by=self.ngo,
        )
        self.authenticate(self.institution)
        response = self.client.get(reverse("document-list"))
        rows = response.data["results"] if "results" in response.data else response.data
        self.assertEqual(len(rows), 1)

    def test_uploader_ngo_can_see_own_beneficiary_document(self):
        Document.objects.create(
            beneficiary=self.beneficiary, document_type="government_id",
            file=fake_file(), uploaded_by=self.ngo,
        )
        self.authenticate(self.ngo)
        response = self.client.get(reverse("document-list"))
        rows = response.data["results"] if "results" in response.data else response.data
        self.assertEqual(len(rows), 1)


class DocumentReviewAndDeleteTests(APITestCase):
    def setUp(self):
        self.ngo = make_user("ngo3@example.com", "ngo", "NGO Three")
        self.institution = make_user("inst3@example.com", "institution", "Institution Three")
        self.campaign = Campaign.objects.create(created_by=self.ngo, title="Review Test", goal_amount=1000, status="live")
        self.document = Document.objects.create(
            campaign=self.campaign, document_type="photo", file=fake_file(), uploaded_by=self.ngo,
        )

    def authenticate(self, user):
        response = self.client.post(reverse("auth-login"), {"email": user.email, "password": "correcthorse8"})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def test_institution_can_verify_document(self):
        self.authenticate(self.institution)
        response = self.client.post(reverse("document-review", args=[self.document.id]), {"status": "verified"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.document.refresh_from_db()
        self.assertEqual(self.document.status, "verified")
        self.assertEqual(self.document.verified_by, self.institution)

    def test_ngo_cannot_review_document(self):
        self.authenticate(self.ngo)
        response = self.client.post(reverse("document-review", args=[self.document.id]), {"status": "verified"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_uploader_can_delete_pending_document(self):
        self.authenticate(self.ngo)
        response = self.client.delete(reverse("document-detail", args=[self.document.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_cannot_delete_verified_document(self):
        self.document.status = "verified"
        self.document.verified_by = self.institution
        self.document.save()
        self.authenticate(self.ngo)
        response = self.client.delete(reverse("document-detail", args=[self.document.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
