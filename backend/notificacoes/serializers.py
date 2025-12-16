from rest_framework import serializers

from .models import Notificacao


class NotificacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacao
        fields = [
            "id",
            "tipo",
            "titulo",
            "mensagem",
            "lida",
            "criado_em",
            "agendamento_id",
            "financeiro_id",
        ]
        read_only_fields = ["id", "criado_em"]
