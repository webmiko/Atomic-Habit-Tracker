"""Модели пользователя и профиля API."""

from django.contrib.auth.models import AbstractUser
from django.db import models

from users.managers import UserManager


class User(AbstractUser):
    """Учётная запись с входом по email и настройками оповещений.

    Attributes:
        email: Уникальный логин.
        public_display_name: Имя в публичной ленте привычек (без email).
        notify_by_email: Разрешение на email-напоминания.
        notify_by_telegram: Разрешение на Telegram-напоминания.
        telegram_chat_id: Идентификатор чата после привязки бота (не в API).
    """

    username = None
    email = models.EmailField("email", unique=True)
    public_display_name = models.CharField(
        "отображаемое имя",
        max_length=150,
        blank=True,
        default="",
    )
    notify_by_email = models.BooleanField("оповещения по email", default=True)
    notify_by_telegram = models.BooleanField("оповещения в Telegram", default=False)
    telegram_chat_id = models.CharField(
        "Telegram chat id",
        max_length=64,
        blank=True,
        null=True,
        unique=True,
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"

    def __str__(self) -> str:
        return str(self.email)

    @property
    def telegram_linked(self) -> bool:
        """Возвращает True, если chat_id Telegram сохранён в профиле."""
        return bool(self.telegram_chat_id)
