from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Financeiro
from .serializers import FinanceiroCreateUpdateSerializer, FinanceiroSerializer


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.usuario == request.user


class FinanceiroListCreateView(generics.ListCreateAPIView):
    serializer_class = FinanceiroSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "tipo", "cliente"]

    def get_queryset(self):
        return Financeiro.objects.filter(usuario=self.request.user, ativo=True).order_by("data_vencimento")

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return FinanceiroCreateUpdateSerializer
        return super().get_serializer_class()


class FinanceiroDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FinanceiroSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    queryset = Financeiro.objects.all()

    def get_queryset(self):
        return Financeiro.objects.filter(usuario=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return FinanceiroCreateUpdateSerializer
        return super().get_serializer_class()

    def perform_destroy(self, instance):
        instance.ativo = False
        instance.save()


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def financeiro_hard_delete(request, pk):
    try:
        financeiro = Financeiro.objects.get(id=pk, usuario=request.user)
        financeiro.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Financeiro.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
