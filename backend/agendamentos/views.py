from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Agendamento
from .serializers import AgendamentoCreateUpdateSerializer, AgendamentoSerializer
from notificacoes.tasks import criar_notificacao_agendamento


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.usuario == request.user


class AgendamentoListCreateView(generics.ListCreateAPIView):
    serializer_class = AgendamentoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "cliente"]

    def get_queryset(self):
        return Agendamento.objects.filter(usuario=self.request.user, ativo=True).order_by("data_hora")

    def perform_create(self, serializer):
        instance = serializer.save(usuario=self.request.user)
        criar_notificacao_agendamento.delay(
            str(self.request.user.id),
            str(instance.id),
            instance.cliente.nome,
            instance.data_hora,
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AgendamentoCreateUpdateSerializer
        return super().get_serializer_class()


class AgendamentoDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AgendamentoSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    queryset = Agendamento.objects.all()

    def get_queryset(self):
        return Agendamento.objects.filter(usuario=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return AgendamentoCreateUpdateSerializer
        return super().get_serializer_class()

    def perform_destroy(self, instance):
        instance.ativo = False
        instance.save()


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def agendamento_hard_delete(request, pk):
    try:
        agendamento = Agendamento.objects.get(id=pk, usuario=request.user)
        agendamento.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Agendamento.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
