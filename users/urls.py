"""Маршруты API пользователей."""

from django.urls import path

from users.views import RegisterView, TelegramLinkView, UserMeView

app_name = "users"

urlpatterns = [
    path("users/register/", RegisterView.as_view(), name="register"),
    path("users/me/", UserMeView.as_view(), name="me"),
    path("users/telegram/link/", TelegramLinkView.as_view(), name="telegram-link"),
]
