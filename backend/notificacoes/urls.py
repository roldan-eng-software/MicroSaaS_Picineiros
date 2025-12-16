from django.urls import path

from .views import (
    NotificacaoListView,
    marcar_como_lida,
    marcar_todas_como_lidas,
)

urlpatterns = [
    path("", NotificacaoListView.as_view(), name="notificacao-list"),
    path("<uuid:pk>/marcar-lida/", marcar_como_lida, name="notificacao-marcar-lida"),
    path("marcar-todas-lidas/", marcar_todas_como_lidas, name="notificacao-marcar-todas-lidas"),
]
