import uuid

from django.db import models
from django.utils import timezone

from accounts.models import User
from agendamentos.models import Agendamento
from clientes.models import Cliente


class Financeiro(models.Model):
    class Tipo(models.TextChoices):
        SERVICO = "servico", "Serviço"
        PRODUTO = "produto", "Produto"
        MULTA = "multa", "Multa"
        OUTRO = "outro", "Outro"

    class Status(models.TextChoices):
        PENDENTE = "pendente", "Pendente"
        PAGO = "pago", "Pago"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="financeiros")
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="financeiros")
    agendamento = models.ForeignKey(Agendamento, on_delete=models.SET_NULL, null=True, blank=True, related_name="financeiros")
    tipo = models.CharField(max_length=15, choices=Tipo.choices, default=Tipo.SERVICO)
    descricao = models.CharField(max_length=200, blank=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_vencimento = models.DateField()
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDENTE)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(default=timezone.now)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["usuario", "ativo"]),
            models.Index(fields=["cliente", "ativo"]),
            models.Index(fields=["agendamento", "ativo"]),
            models.Index(fields=["status", "data_vencimento"]),
        ]
        ordering = ["data_vencimento"]

    def __str__(self):
        return f"{self.cliente.nome} - {self.tipo} ({self.valor}) [{self.status}]"
