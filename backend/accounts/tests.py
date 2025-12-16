from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class AuthFlowTests(APITestCase):
    def setUp(self):
        self.user_email = "user@example.com"
        self.password = "strongpass123"
        self.user = User.objects.create_user(
            email=self.user_email, password=self.password, is_email_verified=True
        )
        self.csrf_url = reverse("csrf")
        self.register_url = reverse("register")
        self.email_verify_url = reverse("email-verify")
        self.login_url = reverse("login")
        self.refresh_url = reverse("refresh")
        self.logout_url = reverse("logout")
        self.me_url = reverse("me")
        self.password_change_url = reverse("password-change")
        self.password_reset_request_url = reverse("password-reset-request")
        self.password_reset_confirm_url = reverse("password-reset-confirm")

    def _get_csrf_client(self):
        client = APIClient(enforce_csrf_checks=True)
        # GET to set CSRF cookie and retrieve token
        resp = client.get(self.csrf_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        csrf_token = resp.data.get("csrfToken")
        self.assertTrue(csrf_token)
        client.credentials(HTTP_X_CSRFTOKEN=csrf_token)
        return client

    def test_user_registration(self):
        new_user_email = "newuser@example.com"
        new_user_pass = "anotherstrongpass"
        data = {
            "email": new_user_email,
            "password": new_user_pass,
            "nome": "Test User",
            "telefone": "123456789",
        }
        resp = self.client.post(self.register_url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn("Verifique seu email", resp.data["detail"])

        # Verify user exists in the database but is not verified
        self.assertTrue(User.objects.filter(email=new_user_email).exists())
        user = User.objects.get(email=new_user_email)
        self.assertFalse(user.is_email_verified)

    def test_email_verification_flow(self):
        # 1. Register a new user
        new_user_email = "verify@example.com"
        new_user_pass = "verifypassword"
        reg_data = {"email": new_user_email, "password": new_user_pass}
        reg_resp = self.client.post(self.register_url, reg_data, format="json")
        self.assertEqual(reg_resp.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email=new_user_email)
        self.assertFalse(user.is_email_verified)

        # 2. Try to login before verification (should fail)
        csrf_client = self._get_csrf_client()
        login_fail_resp = csrf_client.post(self.login_url, reg_data, format="json")
        self.assertEqual(login_fail_resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("Email não verificado", login_fail_resp.data["detail"])

        # 3. Verify email
        token = default_token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        verify_data = {"uidb64": uidb64, "token": token}
        verify_resp = self.client.post(self.email_verify_url, verify_data, format="json")
        self.assertEqual(verify_resp.status_code, status.HTTP_200_OK)

        # 4. Check user is now verified
        user.refresh_from_db()
        self.assertTrue(user.is_email_verified)

        # 5. Try to login again (should succeed)
        login_success_resp = csrf_client.post(self.login_url, reg_data, format="json")
        self.assertEqual(login_success_resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", login_success_resp.data)

    def test_password_change(self):
        new_password = "a_super_new_password"
        # 1. Login to get auth token
        csrf_client = self._get_csrf_client()
        login_resp = csrf_client.post(self.login_url, {"email": self.user_email, "password": self.password}, format="json")
        self.assertEqual(login_resp.status_code, status.HTTP_200_OK)
        access_token = login_resp.data["access"]

        # 2. Change password
        csrf_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        change_resp = csrf_client.post(
            self.password_change_url,
            {"old_password": self.password, "new_password": new_password},
            format="json",
        )
        self.assertEqual(change_resp.status_code, status.HTTP_200_OK)

        # 3. Verify new password works
        new_csrf_client = self._get_csrf_client()
        login_resp_new = new_csrf_client.post(
            self.login_url, {"email": self.user_email, "password": new_password}, format="json"
        )
        self.assertEqual(login_resp_new.status_code, status.HTTP_200_OK)

    def test_password_reset_flow(self):
        # 1. Request password reset
        resp = self.client.post(self.password_reset_request_url, {"email": self.user_email}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # TODO: Mock email backend to check email content for the reset link

        # 2. Confirm password reset
        new_password = "a_brand_new_password"
        token = default_token_generator.make_token(self.user)
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        confirm_data = {"uidb64": uidb64, "token": token, "new_password": new_password}
        resp = self.client.post(self.password_reset_confirm_url, confirm_data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # 3. Verify old password no longer works
        client = self._get_csrf_client()
        login_resp_old = client.post(self.login_url, {"email": self.user_email, "password": self.password}, format="json")
        self.assertEqual(login_resp_old.status_code, status.HTTP_401_UNAUTHORIZED)

        # 4. Verify new password works
        login_resp_new = client.post(self.login_url, {"email": self.user_email, "password": new_password}, format="json")
        self.assertEqual(login_resp_new.status_code, status.HTTP_200_OK)

    def test_login_refresh_logout_flow(self):
        # Login requires CSRF
        client = self._get_csrf_client()

        # Perform login
        resp = client.post(self.login_url, {"email": self.user_email, "password": self.password}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp.data)
        access_token = resp.data["access"]

        # Cookie refresh_token should be set
        self.assertIn("refresh_token", client.cookies)
        refresh_cookie = client.cookies.get("refresh_token")
        self.assertIsNotNone(refresh_cookie)
        self.assertTrue(refresh_cookie.value)

        # Access protected endpoint `me`
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        me_resp = client.get(self.me_url)
        self.assertEqual(me_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(me_resp.data["email"].lower(), self.user_email)

        # Refresh token: requires CSRF and refresh cookie
        client.credentials(HTTP_X_CSRFTOKEN=client._credentials.get("HTTP_X_CSRFTOKEN"))
        refresh_resp = client.post(self.refresh_url)
        self.assertEqual(refresh_resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_resp.data)

        # Logout should delete refresh cookie
        logout_resp = client.post(self.logout_url)
        self.assertEqual(logout_resp.status_code, status.HTTP_204_NO_CONTENT)

        client.cookies.pop("refresh_token", None)
        refresh_resp2 = client.post(self.refresh_url)
        self.assertEqual(refresh_resp2.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_requires_csrf(self):
        client = APIClient(enforce_csrf_checks=True)
        resp = client.post(self.login_url, {"email": self.user_email, "password": self.password}, format="json")
        self.assertIn(resp.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED))

    def test_refresh_requires_cookie(self):
        client = self._get_csrf_client()
        resp = client.post(self.refresh_url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_requires_auth(self):
        client = APIClient()
        resp = client.get(self.me_url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
