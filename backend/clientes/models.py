import uuid

from django.db import models
from django.utils import timezone

from accounts.models import User


class Cliente(models.Model):
    class TipoPiscina(models.TextChoices):
        RESIDENCIAL = "residencial", "Residencial"
        COMERCIAL = "comercial", "Comercial"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="clientes")
    nome = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    telefone = models.CharField(max_length=30, blank=True)
    endereco = models.TextField(blank=True)
    tipo_piscina = models.CharField(
        max_length=20,
        choices=TipoPiscina.choices,
        default=TipoPiscina.RESIDENCIAL,
    )
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(default=timezone.now)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["usuario", "ativo"]),
            models.Index(fields=["nome"]),
        ]

    def __str__(self):
        return f"{self.nome} ({self.usuario.email})"
