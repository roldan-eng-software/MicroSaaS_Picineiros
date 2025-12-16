from django.urls import path

from .views import (
    csrf_view,
    email_verify_view,
    login_view,
    logout_view,
    me_view,
    password_change_view,
    password_reset_confirm_view,
    password_reset_request_view,
    refresh_view,
    register_view,
)

urlpatterns = [
    path("csrf/", csrf_view, name="csrf"),
    path("register/", register_view, name="register"),
    path("email-verify/", email_verify_view, name="email-verify"),
    path("login/", login_view, name="login"),
    path("refresh/", refresh_view, name="refresh"),
    path("logout/", logout_view, name="logout"),
    path("me/", me_view, name="me"),
    path("password-change/", password_change_view, name="password-change"),
    path("password-reset/", password_reset_request_view, name="password-reset-request"),
    path("password-reset/confirm/", password_reset_confirm_view, name="password-reset-confirm"),
]
