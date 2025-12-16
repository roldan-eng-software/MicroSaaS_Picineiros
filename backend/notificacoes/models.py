import uuid

from django.db import models
from django.utils import timezone

from accounts.models import User


class Notificacao(models.Model):
    class Tipo(models.TextChoices):
        AGENDAMENTO_CRIADO = "agendamento_criado", "Agendamento Criado"
        AGENDAMENTO_LEMBRETE = "agendamento_lembrete", "Lembrete de Agendamento"
        FINANCEIRO_VENCIMENTO = "financeiro_vencimento", "Vencimento Financeiro"
        FINANCEIRO_VENCIDO = "financeiro_vencido", "Financeiro Vencido"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notificacoes")
    tipo = models.CharField(max_length=30, choices=Tipo.choices)
    titulo = models.CharField(max_length=200)
    mensagem = models.TextField()
    lida = models.BooleanField(default=False)
    criado_em = models.DateTimeField(default=timezone.now)
    agendamento_id = models.UUIDField(null=True, blank=True)
    financeiro_id = models.UUIDField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["usuario", "lida"]),
            models.Index(fields=["criado_em"]),
        ]
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.usuario.email} - {self.titulo}"
