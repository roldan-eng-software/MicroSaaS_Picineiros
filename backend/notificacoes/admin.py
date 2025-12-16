from django.contrib import admin

from .models import Notificacao


@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ("usuario", "tipo", "titulo", "lida", "criado_em")
    list_filter = ("tipo", "lida", "usuario")
    search_fields = ("titulo", "mensagem")
    readonly_fields = ("id", "criado_em")
    fieldsets = (
        (None, {"fields": ("id", "usuario", "tipo", "titulo", "mensagem")}),
        ("Relacionados", {"fields": ("agendamento_id", "financeiro_id")}),
        ("Status", {"fields": ("lida",)}),
        ("Datas", {"fields": ("criado_em",)}),
    )
