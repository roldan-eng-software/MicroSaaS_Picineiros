from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from clientes.models import Cliente
from .models import Financeiro

User = get_user_model()


class FinanceiroCrudTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="owner@example.com", password="strongpass123")
        self.other = User.objects.create_user(email="other@example.com", password="strongpass123")
        self.list_url = "/api/financeiro/"
        self.cliente = Cliente.objects.create(usuario=self.user, nome="Cliente A")

    def auth(self, user):
        client = APIClient()
        client.force_authenticate(user=user)
        return client

    def test_create_list_ownership_and_soft_delete(self):
        c = self.auth(self.user)
        payload = {
            "cliente": str(self.cliente.id),
            "valor": "199.90",
            "descricao": "Mensalidade",
            "status": "pendente",
        }
        resp = c.post(self.list_url, payload, format="json")
        self.assertIn(resp.status_code, (status.HTTP_201_CREATED, status.HTTP_200_OK))
        fid = resp.data["id"]

        # Owner list
        resp2 = c.get(self.list_url)
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp2.data), 1)

        # Other user sees none
        c2 = self.auth(self.other)
        resp3 = c2.get(self.list_url)
        self.assertEqual(len(resp3.data), 0)

        # Update status to pago
        detail_url = f"{self.list_url}{fid}/"
        upd = c.patch(detail_url, {"status": "pago"}, format="json")
        self.assertEqual(upd.status_code, status.HTTP_200_OK)
        self.assertEqual(upd.data["status"], "pago")

        # Soft delete and ensure not listed
        del_resp = c.delete(detail_url)
        self.assertIn(del_resp.status_code, (status.HTTP_204_NO_CONTENT, status.HTTP_200_OK))
        resp4 = c.get(self.list_url)
        self.assertEqual(len(resp4.data), 0)
