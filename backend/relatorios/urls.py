from django.urls import path

from .views import (
    export_agendamentos_csv,
    export_agendamentos_pdf,
    export_clientes_csv,
    export_clientes_pdf,
    export_financeiro_csv,
    export_financeiro_pdf,
)

urlpatterns = [
    path("clientes/csv/", export_clientes_csv, name="export-clientes-csv"),
    path("clientes/pdf/", export_clientes_pdf, name="export-clientes-pdf"),
    path("agendamentos/csv/", export_agendamentos_csv, name="export-agendamentos-csv"),
    path("agendamentos/pdf/", export_agendamentos_pdf, name="export-agendamentos-pdf"),
    path("financeiro/csv/", export_financeiro_csv, name="export-financeiro-csv"),
    path("financeiro/pdf/", export_financeiro_pdf, name="export-financeiro-pdf"),
]
