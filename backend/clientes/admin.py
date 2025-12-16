from django.contrib import admin

from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nome", "email", "telefone", "tipo_piscina", "ativo", "usuario")
    list_filter = ("ativo", "tipo_piscina", "usuario")
    search_fields = ("nome", "email", "telefone")
    autocomplete_fields = ("usuario",)
    readonly_fields = ("id", "criado_em", "atualizado_em")
    fieldsets = (
        (None, {"fields": ("id", "usuario", "nome", "email", "telefone", "endereco", "tipo_piscina")}),
        ("Status", {"fields": ("ativo",)}),
        ("Datas", {"fields": ("criado_em", "atualizado_em")}),
    )
