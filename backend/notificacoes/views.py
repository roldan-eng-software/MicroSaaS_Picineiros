from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Notificacao
from .serializers import NotificacaoSerializer


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.usuario == request.user


class NotificacaoListView(generics.ListAPIView):
    serializer_class = NotificacaoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["tipo", "lida"]

    def get_queryset(self):
        return Notificacao.objects.filter(usuario=self.request.user).order_by("-criado_em")


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def marcar_como_lida(request, pk):
    try:
        notificacao = Notificacao.objects.get(id=pk, usuario=request.user)
        notificacao.lida = True
        notificacao.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Notificacao.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def marcar_todas_como_lidas(request):
    Notificacao.objects.filter(usuario=request.user, lida=False).update(lida=True)
    return Response(status=status.HTTP_204_NO_CONTENT)
