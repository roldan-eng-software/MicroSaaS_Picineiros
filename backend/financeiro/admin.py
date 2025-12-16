from django.contrib import admin

from .models import Financeiro


@admin.register(Financeiro)
class FinanceiroAdmin(admin.ModelAdmin):
    list_display = ("cliente", "tipo", "valor", "data_vencimento", "status", "usuario", "ativo")
    list_filter = ("status", "tipo", "ativo", "usuario")
    search_fields = ("cliente__nome", "descricao")
    autocomplete_fields = ("cliente", "usuario", "agendamento")
    readonly_fields = ("id", "criado_em", "atualizado_em")
    fieldsets = (
        (None, {"fields": ("id", "usuario", "cliente", "agendamento", "tipo", "descricao", "valor", "data_vencimento", "status")}),
        ("Status", {"fields": ("ativo",)}),
        ("Datas", {"fields": ("criado_em", "atualizado_em")}),
    )
