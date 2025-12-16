from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class AuthFlowTests(APITestCase):
    def setUp(self):
        self.user_email = "user@example.com"
        self.password = "strongpass123"
        self.user = User.objects.create_user(email=self.user_email, password=self.password)
        self.csrf_url = reverse("csrf")  # /api/auth/csrf/
        self.login_url = reverse("login")  # /api/auth/login/
        self.refresh_url = reverse("refresh")  # /api/auth/refresh/
        self.logout_url = reverse("logout")  # /api/auth/logout/
        self.me_url = reverse("me")  # /api/auth/me/

    def _get_csrf_client(self):
        client = APIClient(enforce_csrf_checks=True)
        # GET to set CSRF cookie and retrieve token
        resp = client.get(self.csrf_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        csrf_token = resp.data.get("csrfToken")
        self.assertTrue(csrf_token)
        client.credentials(HTTP_X_CSRFTOKEN=csrf_token)
        return client

    def test_login_refresh_logout_flow(self):
        # Login requires CSRF
        client = self._get_csrf_client()

        # Perform login
        resp = client.post(self.login_url, {"email": self.user_email, "password": self.password}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp.data)
        access_token = resp.data["access"]

        # Cookie refresh_token should be set
        # DRF APIClient stores cookies in client.cookies
        self.assertIn("refresh_token", client.cookies)
        refresh_cookie = client.cookies.get("refresh_token")
        self.assertIsNotNone(refresh_cookie)
        self.assertTrue(refresh_cookie.value)

        # Access protected endpoint `me`
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        me_resp = client.get(self.me_url)
        self.assertEqual(me_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(me_resp.data["email"].lower(), self.user_email)

        # Refresh token: requires CSRF and refresh cookie (already present). Reset auth header
        client.credentials(HTTP_X_CSRFTOKEN=client._credentials.get("HTTP_X_CSRFTOKEN"))
        refresh_resp = client.post(self.refresh_url)
        self.assertEqual(refresh_resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_resp.data)

        # Logout should delete refresh cookie
        logout_resp = client.post(self.logout_url)
        self.assertEqual(logout_resp.status_code, status.HTTP_204_NO_CONTENT)
        # After logout, server sets a Set-Cookie header clearing the cookie; APIClient won't auto-remove from jar.
        # We can simulate subsequent call without the cookie to ensure 401 on refresh
        client.cookies.pop("refresh_token", None)
        refresh_resp2 = client.post(self.refresh_url)
        self.assertEqual(refresh_resp2.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_requires_csrf(self):
        # Without CSRF enforcement, login should be blocked by @csrf_protect
        client = APIClient(enforce_csrf_checks=True)
        resp = client.post(self.login_url, {"email": self.user_email, "password": self.password}, format="json")
        self.assertIn(resp.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED))

    def test_refresh_requires_cookie(self):
        client = self._get_csrf_client()
        # No refresh cookie should yield 401
        resp = client.post(self.refresh_url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_requires_auth(self):
        client = APIClient()
        resp = client.get(self.me_url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
