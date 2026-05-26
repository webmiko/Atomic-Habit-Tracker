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

    def save(self, *args: object, **kwargs: object) -> None:
        """Сохраняет пользователя; пустой chat_id храним как NULL (unique)."""
        if self.telegram_chat_id is not None and not str(self.telegram_chat_id).strip():
            self.telegram_chat_id = None
        super().save(*args, **kwargs)

    @property
    def telegram_linked(self) -> bool:
        """Возвращает True, если chat_id Telegram сохранён в профиле."""
        return bool(self.telegram_chat_id)


class TelegramLinkCode(models.Model):
    """Одноразовый код привязки Telegram к аккаунту пользователя.

    Attributes:
        user: Владелец кода.
        code: Строка для команды ``/link`` в боте.
        expires_at: Момент истечения кода (обычно 15 минут).
        created_at: Время создания записи.
    """

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="telegram_link_codes",
        verbose_name="пользователь",
    )
    code = models.CharField("код", max_length=16, unique=True, db_index=True)
    expires_at = models.DateTimeField("истекает")
    created_at = models.DateTimeField("создан", auto_now_add=True)

    class Meta:
        verbose_name = "код привязки Telegram"
        verbose_name_plural = "коды привязки Telegram"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.code} ({self.user_id})"
