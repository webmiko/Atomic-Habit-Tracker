"""Модели пользователя и профиля API."""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Учётная запись с входом по email.

    Attributes:
        email: Уникальный логин и адрес для оповещений.
    """

    username = None
    email = models.EmailField("email", unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"

    def __str__(self) -> str:
        return str(self.email)
