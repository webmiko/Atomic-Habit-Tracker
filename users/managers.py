"""Менеджер queryset для модели User с входом по email."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.base_user import BaseUserManager

if TYPE_CHECKING:
    from users.models import User


class UserManager(BaseUserManager):
    """Создаёт пользователей с обязательным email вместо username."""

    def create_user(
        self,
        email: str,
        password: str | None = None,
        **extra_fields: object,
    ) -> User:
        """Создаёт обычного пользователя.

        Args:
            email: Уникальный адрес электронной почты.
            password: Пароль в открытом виде (хешируется перед сохранением).
            **extra_fields: Дополнительные поля модели User.

        Returns:
            Сохранённый экземпляр User.

        Raises:
            ValueError: Если email пустой.
        """
        from users.models import User as UserModel

        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = UserModel(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email: str,
        password: str | None = None,
        **extra_fields: object,
    ) -> User:
        """Создаёт суперпользователя для админ-панели.

        Args:
            email: Уникальный адрес электронной почты.
            password: Пароль суперпользователя.
            **extra_fields: Дополнительные поля модели User.

        Returns:
            Сохранённый экземпляр User с флагами staff и superuser.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)
