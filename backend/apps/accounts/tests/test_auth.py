from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.tokens import generate_password_reset_token

User = get_user_model()


class RegisterTests(APITestCase):
    def test_register_creates_user_and_returns_tokens(self):
        response = self.client.post(reverse("auth-register"), {
            "full_name": "Sarah Chen",
            "email": "sarah@example.com",
            "password": "correcthorse8",
            "role": "donor",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["username"], "Sarah Chen")
        self.assertEqual(response.data["user"]["role"], "donor")
        self.assertTrue(User.objects.filter(email="sarah@example.com").exists())

    def test_register_rejects_admin_role(self):
        response = self.client.post(reverse("auth-register"), {
            "full_name": "Shouldnt Work",
            "email": "notadmin@example.com",
            "password": "correcthorse8",
            "role": "admin",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email="notadmin@example.com").exists())

    def test_register_rejects_weak_password(self):
        response = self.client.post(reverse("auth-register"), {
            "full_name": "Weak Password",
            "email": "weak@example.com",
            "password": "123",
            "role": "donor",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_rejects_duplicate_email(self):
        User.objects.create_user(email="dupe@example.com", full_name="First", role="donor", password="correcthorse8")
        response = self.client.post(reverse("auth-register"), {
            "full_name": "Second",
            "email": "dupe@example.com",
            "password": "correcthorse8",
            "role": "donor",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="ngo@example.com", full_name="WaterHelp International",
            role="ngo", password="correcthorse8",
        )

    def test_login_success(self):
        response = self.client.post(reverse("auth-login"), {
            "email": "ngo@example.com", "password": "correcthorse8",
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["username"], "WaterHelp International")
        self.assertEqual(response.data["user"]["role"], "ngo")

    def test_login_wrong_password(self):
        response = self.client.post(reverse("auth-login"), {
            "email": "ngo@example.com", "password": "wrongpassword",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_nonexistent_email(self):
        response = self.client.post(reverse("auth-login"), {
            "email": "nobody@example.com", "password": "correcthorse8",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RefreshTests(APITestCase):
    def test_refresh_returns_new_access_token(self):
        User.objects.create_user(email="refresh@example.com", full_name="Refresh Test", role="donor", password="correcthorse8")
        login = self.client.post(reverse("auth-login"), {"email": "refresh@example.com", "password": "correcthorse8"})
        response = self.client.post(reverse("auth-refresh"), {"refresh": login.data["refresh"]})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)


class LogoutTests(APITestCase):
    def test_logout_blacklists_refresh_token(self):
        User.objects.create_user(email="logout@example.com", full_name="Logout Test", role="donor", password="correcthorse8")
        login = self.client.post(reverse("auth-login"), {"email": "logout@example.com", "password": "correcthorse8"})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

        response = self.client.post(reverse("auth-logout"), {"refresh": login.data["refresh"]})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # The now-blacklisted refresh token must be rejected on reuse.
        refresh_attempt = self.client.post(reverse("auth-refresh"), {"refresh": login.data["refresh"]})
        self.assertEqual(refresh_attempt.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_requires_authentication(self):
        response = self.client.post(reverse("auth-logout"), {"refresh": "irrelevant"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class MeTests(APITestCase):
    def test_me_returns_current_user(self):
        User.objects.create_user(email="me@example.com", full_name="Me Test", role="institution", password="correcthorse8")
        login = self.client.post(reverse("auth-login"), {"email": "me@example.com", "password": "correcthorse8"})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

        response = self.client.get(reverse("auth-me"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "Me Test")
        self.assertEqual(response.data["role"], "institution")

    def test_me_requires_authentication(self):
        response = self.client.get(reverse("auth-me"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PasswordResetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="reset@example.com", full_name="Reset Test", role="donor", password="oldpassword8",
        )

    def test_request_always_returns_200_even_for_unknown_email(self):
        known = self.client.post(reverse("auth-password-reset"), {"email": "reset@example.com"})
        unknown = self.client.post(reverse("auth-password-reset"), {"email": "nobody@example.com"})
        self.assertEqual(known.status_code, status.HTTP_200_OK)
        self.assertEqual(unknown.status_code, status.HTTP_200_OK)

    def test_confirm_with_valid_token_changes_password(self):
        token = generate_password_reset_token(str(self.user.id))
        response = self.client.post(reverse("auth-password-reset-confirm"), {
            "token": token, "new_password": "newpassword8",
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        login = self.client.post(reverse("auth-login"), {"email": "reset@example.com", "password": "newpassword8"})
        self.assertEqual(login.status_code, status.HTTP_200_OK)

    def test_confirm_with_invalid_token_fails(self):
        response = self.client.post(reverse("auth-password-reset-confirm"), {
            "token": "not-a-real-token", "new_password": "newpassword8",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
