"""Приложение Django для учётных записей и JWT."""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Конфигурация приложения users."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "users"
    verbose_name = "Пользователи"
