from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .models import Cliente

User = get_user_model()


class ClientesCrudTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="owner@example.com", password="strongpass123")
        self.other = User.objects.create_user(email="other@example.com", password="strongpass123")
        self.list_url = reverse("clientes-list")  # expecting router names
        # Fallback if not using DRF router naming
        if not self.list_url:
            self.list_url = "/api/clientes/"

    def auth(self, user):
        client = APIClient()
        client.force_authenticate(user=user)
        return client

    def test_create_list_ownership(self):
        c = self.auth(self.user)
        payload = {"nome": "Cliente A", "telefone": "11999999999", "tipo_piscina": "residencial"}
        resp = c.post(self.list_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        cid = resp.data["id"]

        # List only returns user's
        resp2 = c.get(self.list_url)
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp2.data), 1)

        # Other user can't see
        c2 = self.auth(self.other)
        resp3 = c2.get(self.list_url)
        self.assertEqual(resp3.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp3.data), 0)

        # Retrieve/Update/Delete restricted
        detail_url = f"{self.list_url}{cid}/"
        resp4 = c2.get(detail_url)
        self.assertIn(resp4.status_code, (status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN))

        # Soft delete
        del_resp = self.auth(self.user).delete(detail_url)
        self.assertIn(del_resp.status_code, (status.HTTP_204_NO_CONTENT, status.HTTP_200_OK))
        # After delete, should not appear
        resp5 = self.auth(self.user).get(self.list_url)
        self.assertEqual(len(resp5.data), 0)
