from django.urls import path

from .views import (
    ClienteDetailView,
    ClienteListCreateView,
    cliente_hard_delete,
)

urlpatterns = [
    path("", ClienteListCreateView.as_view(), name="cliente-list-create"),
    path("<uuid:pk>/", ClienteDetailView.as_view(), name="cliente-detail"),
    path("<uuid:pk>/hard-delete/", cliente_hard_delete, name="cliente-hard-delete"),
]
