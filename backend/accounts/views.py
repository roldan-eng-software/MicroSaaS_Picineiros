import logging

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import LoginSerializer, MeSerializer

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
