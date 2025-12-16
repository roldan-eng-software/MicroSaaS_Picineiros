from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from agendamentos.models import Agendamento
from clientes.models import Cliente
from financeiro.models import Financeiro


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats(request):
    user = request.user

    # Totais
    total_clientes = Cliente.objects.filter(usuario=user, ativo=True).count()
    total_agendamentos = Agendamento.objects.filter(usuario=user, ativo=True).count()
    total_financeiro = Financeiro.objects.filter(usuario=user, ativo=True).count()

    # Financeiro
    financeiro_pendente = Financeiro.objects.filter(usuario=user, ativo=True, status="pendente").aggregate(total=Sum("valor"))["total"] or 0
    financeiro_pago = Financeiro.objects.filter(usuario=user, ativo=True, status="pago").aggregate(total=Sum("valor"))["total"] or 0

    # Próximos agendamentos (próximos 7 dias)
    sete_dias = timezone.now() + timezone.timedelta(days=7)
    proximos_agendamentos = Agendamento.objects.filter(
        usuario=user, ativo=True, data_hora__lte=sete_dias, data_hora__gte=timezone.now()
    ).order_by("data_hora")[:5]

    proximos_agendamentos_data = [
        {
            "id": str(a.id),
            "cliente_nome": a.cliente.nome,
            "data_hora": a.data_hora.isoformat(),
            "status": a.status,
        }
        for a in proximos_agendamentos
    ]

    # Receita mensal (últimos 6 meses) - compatível com Postgres/SQLite
    seis_meses_atras = timezone.now() - timezone.timedelta(days=180)
    receita_mensal = (
        Financeiro.objects.filter(
            usuario=user,
            ativo=True,
            status="pago",
            criado_em__gte=seis_meses_atras,
        )
        .annotate(month=TruncMonth("criado_em"))
        .values("month")
        .annotate(total=Sum("valor"))
        .order_by("month")
    )
    receita_mensal_data = [
        {
            "mes": r["month"].strftime("%Y-%m") if hasattr(r["month"], "strftime") else str(r["month"]),
            "valor": float(r["total"]),
        }
        for r in receita_mensal
    ]

    # Financeiro por status
    financeiro_por_status = (
        Financeiro.objects.filter(usuario=user, ativo=True)
        .values("status")
        .annotate(total=Sum("valor"))
        .order_by("status")
    )
    financeiro_por_status_data = [
        {"status": r["status"], "valor": float(r["total"])} for r in financeiro_por_status
    ]

    return Response(
        {
            "totais": {
                "clientes": total_clientes,
                "agendamentos": total_agendamentos,
                "financeiro": total_financeiro,
            },
            "financeiro": {
                "pendente": float(financeiro_pendente),
                "pago": float(financeiro_pago),
            },
            "proximos_agendamentos": proximos_agendamentos_data,
            "receita_mensal": receita_mensal_data,
            "financeiro_por_status": financeiro_por_status_data,
        }
    )
