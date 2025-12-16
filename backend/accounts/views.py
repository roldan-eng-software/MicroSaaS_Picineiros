import logging

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.middleware.csrf import get_token
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    LoginSerializer,
    MeSerializer,
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    UserCreateSerializer,
)

logger = logging.getLogger("accounts")
User = get_user_model()


def _refresh_cookie_kwargs(request):
    secure = not settings.DEBUG
    return {
        "httponly": True,
        "secure": secure,
        "samesite": "Lax",
        "path": "/api/auth/",
    }


@api_view(["GET"])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def csrf_view(request):
    token = get_token(request)
    return Response({"csrfToken": token})


@api_view(["POST"])
@permission_classes([AllowAny])
def register_view(request):
    serializer = UserCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()

    # Send verification email
    token = default_token_generator.make_token(user)
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    verify_link = f"{settings.FRONTEND_ORIGIN}/verify-email/{uidb64}/{token}"

    send_mail(
        "Verifique seu email",
        f"Use o link a seguir para verificar seu endereço de email: {verify_link}",
        "noreply@picineiros.com",
        [user.email],
        fail_silently=False,
    )
    return Response(
        {"detail": "Usuário registrado com sucesso. Verifique seu email para ativar sua conta."},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def email_verify_view(request):
    # This view is simplified and assumes uidb64 and token are in the body.
    # A GET request with URL params might be more conventional.
    uidb64 = request.data.get("uidb64")
    token = request.data.get("token")

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if not user.is_email_verified:
            user.is_email_verified = True
            user.save()
        return Response({"detail": "Email verificado com sucesso."}, status=status.HTTP_200_OK)
    else:
        return Response({"detail": "Link inválido ou expirado."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_request_view(request):
    serializer = PasswordResetRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data["email"]

    try:
        user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        user = None

    if user:
        token = default_token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = f"{settings.FRONTEND_ORIGIN}/reset-password/{uidb64}/{token}"

        send_mail(
            "Seu link para redefinição de senha",
            f"Use o link a seguir para redefinir sua senha: {reset_link}",
            "noreply@picineiros.com",
            [user.email],
            fail_silently=False,
        )

    return Response(
        {"detail": "Se um usuário com este email existir, um link de redefinição de senha foi enviado."},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_confirm_view(request):
    serializer = PasswordResetConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    try:
        uid = urlsafe_base64_decode(data["uidb64"]).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, data["token"]):
        user.set_password(data["new_password"])
        user.save()
        return Response({"detail": "Senha redefinida com sucesso."}, status=status.HTTP_200_OK)
    else:
        return Response({"detail": "Link inválido ou expirado."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([ScopedRateThrottle])
@csrf_protect
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data["email"].lower()
    password = serializer.validated_data["password"]

    user = authenticate(request, username=email, password=password)
    if not user:
        logger.info("login_failed", extra={"email": email, "ip": request.META.get("REMOTE_ADDR")})
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    if not getattr(user, "is_active", True):
        logger.info("login_inactive_user", extra={"user_id": str(user.id)})
        return Response({"detail": "User inactive"}, status=status.HTTP_403_FORBIDDEN)
    
    if not user.is_email_verified:
        logger.info("login_unverified_email", extra={"user_id": str(user.id)})
        return Response({"detail": "Email não verificado."}, status=status.HTTP_403_FORBIDDEN)

    refresh = RefreshToken.for_user(user)
    access = str(refresh.access_token)

    resp = Response({"access": access}, status=status.HTTP_200_OK)
    resp.set_cookie(settings.REFRESH_COOKIE_NAME, str(refresh), **_refresh_cookie_kwargs(request))
    return resp


login_view.throttle_scope = "login"


@api_view(["POST"])
@permission_classes([AllowAny])
@csrf_protect
def refresh_view(request):
    refresh_token = request.COOKIES.get(settings.REFRESH_COOKIE_NAME)
    if not refresh_token:
        return Response({"detail": "Missing refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        token = RefreshToken(refresh_token)
        user_id = token.get("user_id")
        user = User.objects.get(id=user_id)
    except Exception:
        logger.info("refresh_failed", extra={"ip": request.META.get("REMOTE_ADDR")})
        return Response({"detail": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

    new_refresh = RefreshToken.for_user(user)
    access = str(new_refresh.access_token)

    resp = Response({"access": access}, status=status.HTTP_200_OK)
    resp.set_cookie(settings.REFRESH_COOKIE_NAME, str(new_refresh), **_refresh_cookie_kwargs(request))
    return resp


@api_view(["POST"])
@permission_classes([AllowAny])
@csrf_protect
def logout_view(request):
    resp = Response(status=status.HTTP_204_NO_CONTENT)
    resp.delete_cookie(settings.REFRESH_COOKIE_NAME, path="/api/auth/")
    return resp


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_view(request):
    return Response(MeSerializer(request.user).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def password_change_view(request):
    serializer = PasswordChangeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = request.user
    old_password = serializer.validated_data["old_password"]
    new_password = serializer.validated_data["new_password"]

    if not user.check_password(old_password):
        return Response({"detail": "Senha antiga incorreta."}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()
    return Response({"detail": "Senha alterada com sucesso."}, status=status.HTTP_200_OK)
