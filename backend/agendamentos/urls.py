from django.urls import path

from .views import (
    AgendamentoDetailView,
    AgendamentoListCreateView,
    agendamento_hard_delete,
)

urlpatterns = [
    path("", AgendamentoListCreateView.as_view(), name="agendamento-list-create"),
    path("<uuid:pk>/", AgendamentoDetailView.as_view(), name="agendamento-detail"),
    path("<uuid:pk>/hard-delete/", agendamento_hard_delete, name="agendamento-hard-delete"),
]
