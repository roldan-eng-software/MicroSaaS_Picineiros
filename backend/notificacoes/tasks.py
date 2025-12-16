from celery import shared_task
from django.utils import timezone

from .models import Notificacao


@shared_task
def criar_notificacao_agendamento(usuario_id, agendamento_id, cliente_nome, data_hora):
    from accounts.models import User
    usuario = User.objects.get(id=usuario_id)
    Notificacao.objects.create(
        usuario=usuario,
        tipo=Notificacao.Tipo.AGENDAMENTO_CRIADO,
        titulo="Novo Agendamento Criado",
        mensagem=f"Agendamento para {cliente_nome} em {data_hora.strftime('%d/%m/%Y %H:%M')}",
        agendamento_id=agendamento_id,
    )


@shared_task
def criar_notificacao_lembrete_agendamento():
    from agendamentos.models import Agendamento
    amanha = timezone.now().date() + timezone.timedelta(days=1)
    agendamentos = Agendamento.objects.filter(
        data_hora__date=amanha, ativo=True, status="pendente"
    )
    for ag in agendamentos:
        Notificacao.objects.get_or_create(
            usuario=ag.usuario,
            tipo=Notificacao.Tipo.AGENDAMENTO_LEMBRETE,
            agendamento_id=ag.id,
            defaults={
                "titulo": "Lembrete de Agendamento",
                "mensagem": f"Amanhã: {ag.cliente.nome} às {ag.data_hora.strftime('%H:%M')}",
            },
        )


@shared_task
def criar_notificacoes_vencimento():
    from financeiro.models import Financeiro
    hoje = timezone.now().date()
    proximos_3_dias = hoje + timezone.timedelta(days=3)
    financeiros = Financeiro.objects.filter(
        data_vencimento__lte=proximos_3_dias,
        data_vencimento__gte=hoje,
        ativo=True,
        status="pendente",
    )
    for f in financeiros:
        tipo = (
            Notificacao.Tipo.FINANCEIRO_VENCIDO
            if f.data_vencimento <= hoje
            else Notificacao.Tipo.FINANCEIRO_VENCIMENTO
        )
        Notificacao.objects.get_or_create(
            usuario=f.usuario,
            tipo=tipo,
            financeiro_id=f.id,
            defaults={
                "titulo": "Vencimento Financeiro"
                if tipo == Notificacao.Tipo.FINANCEIRO_VENCIMENTO
                else "Financeiro Vencido",
                "mensagem": f"{f.cliente.nome} - R$ {f.valor:.2f} - Vencimento: {f.data_vencimento.strftime('%d/%m/%Y')}",
            },
        )
