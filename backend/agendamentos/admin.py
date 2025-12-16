from django.contrib import admin

from .models import Agendamento


@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ("cliente", "data_hora", "status", "usuario", "ativo")
    list_filter = ("status", "ativo", "usuario")
    search_fields = ("cliente__nome", "observacoes")
    autocomplete_fields = ("cliente", "usuario")
    readonly_fields = ("id", "criado_em", "atualizado_em")
    fieldsets = (
        (None, {"fields": ("id", "usuario", "cliente", "data_hora", "status", "observacoes")}),
        ("Status", {"fields": ("ativo",)}),
        ("Datas", {"fields": ("criado_em", "atualizado_em")}),
    )
