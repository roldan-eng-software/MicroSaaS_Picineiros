from rest_framework import serializers

from .models import Financeiro


class FinanceiroSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.CharField(source="cliente.nome", read_only=True)

    class Meta:
        model = Financeiro
        fields = [
            "id",
            "cliente",
            "cliente_nome",
            "agendamento",
            "tipo",
            "descricao",
            "valor",
            "data_vencimento",
            "status",
            "ativo",
            "criado_em",
            "atualizado_em",
        ]
        read_only_fields = ["id", "criado_em", "atualizado_em"]


class FinanceiroCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Financeiro
        fields = ["cliente", "agendamento", "tipo", "descricao", "valor", "data_vencimento", "status"]
        extra_kwargs = {
            "cliente": {"required": True},
            "valor": {"required": True},
            "data_vencimento": {"required": True},
        }
