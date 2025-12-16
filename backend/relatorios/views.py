import csv
import io

from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes

from agendamentos.models import Agendamento
from clientes.models import Cliente
from financeiro.models import Financeiro


def csv_response(filename: str, rows: list[list[str]], headers: list[str]) -> HttpResponse:
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow(headers)
    writer.writerows(rows)
    return response


def pdf_response(filename: str, title: str, headers: list[str], rows: list[list[str]]) -> HttpResponse:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(title, styles["Title"]))
    elements.append(Paragraph(" ", styles["Normal"]))

    table = Table([headers] + rows, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), "#dddddd"),
        ("TEXTCOLOR", (0, 0), (-1, 0), (0, 0, 0)),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("BACKGROUND", (0, 1), (-1, -1), "#f6f6f6"),
        ("GRID", (0, 0), (-1, -1), 1, "#000000"),
    ]))
    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def export_clientes_csv(request):
    qs = Cliente.objects.filter(usuario=request.user, ativo=True).order_by("nome")
    rows = [[c.nome, c.email or "", c.telefone or "", c.endereco or "", c.tipo_piscina] for c in qs]
    headers = ["Nome", "Email", "Telefone", "Endereço", "Tipo de Piscina"]
    return csv_response("clientes.csv", rows, headers)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def export_clientes_pdf(request):
    qs = Cliente.objects.filter(usuario=request.user, ativo=True).order_by("nome")
    rows = [[c.nome, c.email or "", c.telefone or "", c.endereco or "", c.tipo_piscina] for c in qs]
    headers = ["Nome", "Email", "Telefone", "Endereço", "Tipo de Piscina"]
    return pdf_response("clientes.pdf", "Relatório de Clientes", headers, rows)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def export_agendamentos_csv(request):
    qs = Agendamento.objects.filter(usuario=request.user, ativo=True).order_by("data_hora")
    rows = [
        [
            a.cliente.nome,
            a.data_hora.strftime("%d/%m/%Y %H:%M"),
            a.status,
            a.observacoes or "",
        ]
        for a in qs
    ]
    headers = ["Cliente", "Data/Hora", "Status", "Observações"]
    return csv_response("agendamentos.csv", rows, headers)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def export_agendamentos_pdf(request):
    qs = Agendamento.objects.filter(usuario=request.user, ativo=True).order_by("data_hora")
    rows = [
        [
            a.cliente.nome,
            a.data_hora.strftime("%d/%m/%Y %H:%M"),
            a.status,
            a.observacoes or "",
        ]
        for a in qs
    ]
    headers = ["Cliente", "Data/Hora", "Status", "Observações"]
    return pdf_response("agendamentos.pdf", "Relatório de Agendamentos", headers, rows)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def export_financeiro_csv(request):
    qs = Financeiro.objects.filter(usuario=request.user, ativo=True).order_by("data_vencimento")
    rows = [
        [
            f.cliente.nome,
            f.tipo,
            f.descricao or "",
            f"R$ {f.valor:.2f}",
            f.data_vencimento.strftime("%d/%m/%Y"),
            f.status,
        ]
        for f in qs
    ]
    headers = ["Cliente", "Tipo", "Descrição", "Valor", "Vencimento", "Status"]
    return csv_response("financeiro.csv", rows, headers)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def export_financeiro_pdf(request):
    qs = Financeiro.objects.filter(usuario=request.user, ativo=True).order_by("data_vencimento")
    rows = [
        [
            f.cliente.nome,
            f.tipo,
            f.descricao or "",
            f"R$ {f.valor:.2f}",
            f.data_vencimento.strftime("%d/%m/%Y"),
            f.status,
        ]
        for f in qs
    ]
    headers = ["Cliente", "Tipo", "Descrição", "Valor", "Vencimento", "Status"]
    return pdf_response("financeiro.pdf", "Relatório Financeiro", headers, rows)
