from rest_framework import serializers

from .models import Agendamento


class AgendamentoSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.CharField(source="cliente.nome", read_only=True)

    class Meta:
        model = Agendamento
        fields = [
            "id",
            "cliente",
            "cliente_nome",
            "data_hora",
            "status",
            "observacoes",
            "ativo",
            "criado_em",
            "atualizado_em",
        ]
        read_only_fields = ["id", "criado_em", "atualizado_em"]


class AgendamentoCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agendamento
        fields = ["cliente", "data_hora", "status", "observacoes"]
        extra_kwargs = {
            "cliente": {"required": True},
            "data_hora": {"required": True},
        }
