from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Cliente
from .serializers import ClienteCreateUpdateSerializer, ClienteSerializer


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.usuario == request.user


class ClienteListCreateView(generics.ListCreateAPIView):
    serializer_class = ClienteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["ativo", "tipo_piscina"]

    def get_queryset(self):
        return Cliente.objects.filter(usuario=self.request.user, ativo=True).order_by("-criado_em")

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ClienteCreateUpdateSerializer
        return super().get_serializer_class()


class ClienteDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ClienteSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    queryset = Cliente.objects.all()

    def get_queryset(self):
        return Cliente.objects.filter(usuario=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return ClienteCreateUpdateSerializer
        return super().get_serializer_class()

    def perform_destroy(self, instance):
        instance.ativo = False
        instance.save()


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def cliente_hard_delete(request, pk):
    try:
        cliente = Cliente.objects.get(id=pk, usuario=request.user)
        cliente.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Cliente.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
