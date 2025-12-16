from django.urls import path

from .views import (
    FinanceiroDetailView,
    FinanceiroListCreateView,
    financeiro_hard_delete,
)

urlpatterns = [
    path("", FinanceiroListCreateView.as_view(), name="financeiro-list-create"),
    path("<uuid:pk>/", FinanceiroDetailView.as_view(), name="financeiro-detail"),
    path("<uuid:pk>/hard-delete/", financeiro_hard_delete, name="financeiro-hard-delete"),
]
