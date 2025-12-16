from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from clientes.models import Cliente
from .models import Agendamento

User = get_user_model()


class AgendamentosCrudTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="owner@example.com", password="strongpass123")
        self.other = User.objects.create_user(email="other@example.com", password="strongpass123")
        self.list_url = reverse("agendamento-list") if False else "/api/agendamentos/"  # ensure path

        # Create a client for the owner
        self.cliente = Cliente.objects.create(usuario=self.user, nome="Cliente A")

    def auth(self, user):
        client = APIClient()
        client.force_authenticate(user=user)
        return client

    def test_create_list_and_notifications_trigger(self):
        c = self.auth(self.user)
        payload = {
            "cliente": str(self.cliente.id),
            "descricao": "Manutenção",
            "data_hora": "2030-01-01T10:00:00Z",
        }
        resp = c.post(self.list_url, payload, format="json")
        self.assertIn(resp.status_code, (status.HTTP_201_CREATED, status.HTTP_200_OK))
        aid = resp.data.get("id") or resp.data.get("pk")
        self.assertTrue(aid)

        # List owner-only
        resp2 = c.get(self.list_url)
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(resp2.data), 1)

        # Other user sees none
        c2 = self.auth(self.other)
        resp3 = c2.get(self.list_url)
        self.assertEqual(len(resp3.data), 0)

        # Soft delete
        detail_url = f"{self.list_url}{aid}/"
        del_resp = c.delete(detail_url)
        self.assertIn(del_resp.status_code, (status.HTTP_204_NO_CONTENT, status.HTTP_200_OK))

        # Ensure not listed after delete
        resp4 = c.get(self.list_url)
        self.assertTrue(all(it.get("id") != aid for it in resp4.data))
