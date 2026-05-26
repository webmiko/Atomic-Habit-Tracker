"""Приложение Django для привычек и напоминаний."""

from django.apps import AppConfig


class HabitsConfig(AppConfig):
    """Конфигурация приложения habits."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "habits"
    verbose_name = "Привычки"
