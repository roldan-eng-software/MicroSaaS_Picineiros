from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase
from clientes.models import Cliente
from agendamentos.models import Agendamento
from financeiro.models import Financeiro
from .models import Notificacao
from .tasks import criar_notificacao_lembrete_agendamento, criar_notificacoes_vencimento

User = get_user_model()


class NotificacoesTasksTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="owner@example.com", password="strongpass123")
        self.cliente = Cliente.objects.create(usuario=self.user, nome="Cliente A")

    def test_task_criar_lembrete_agendamento(self):
        # Agendamento para amanhã
        tomorrow = timezone.now() + timezone.timedelta(days=1)
        Agendamento.objects.create(usuario=self.user, cliente=self.cliente, data_hora=tomorrow, descricao="Serviço")
        criar_notificacao_lembrete_agendamento()
        self.assertTrue(Notificacao.objects.filter(usuario=self.user, tipo="agendamento_lembrete").exists())

    def test_task_criar_notificacoes_vencimento(self):
        # Financeiro vencendo hoje e vencido até 3 dias
        Financeiro.objects.create(usuario=self.user, cliente=self.cliente, valor=100, status="pendente", vencimento=timezone.now().date())
        Financeiro.objects.create(usuario=self.user, cliente=self.cliente, valor=200, status="pendente", vencimento=(timezone.now() - timezone.timedelta(days=2)).date())
        criar_notificacoes_vencimento()
        self.assertTrue(Notificacao.objects.filter(usuario=self.user, tipo__in=["financeiro_vencimento", "financeiro_vencido"]).exists())
