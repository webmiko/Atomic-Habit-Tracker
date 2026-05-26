"""Тесты UserManager."""

import pytest

from users.models import User


@pytest.mark.django_db
def test_create_user_requires_email() -> None:
    """create_user без email поднимает ValueError."""
    with pytest.raises(ValueError, match="Email"):
        User.objects.create_user(email="", password="StrongPass123!")


@pytest.mark.django_db
def test_create_superuser_sets_flags() -> None:
    """create_superuser создаёт staff и superuser."""
    admin = User.objects.create_superuser(
        email="admin@example.com",
        password="StrongPass123!",
    )
    assert admin.is_staff
    assert admin.is_superuser
    assert admin.is_active


@pytest.mark.django_db
def test_empty_telegram_chat_id_saved_as_null() -> None:
    """Пустой chat_id не ломает unique — в БД хранится NULL."""
    from users.models import User

    first = User.objects.create_user(email="tg1@example.com", password="StrongPass123!")
    second = User.objects.create_user(email="tg2@example.com", password="StrongPass123!")
    first.telegram_chat_id = ""
    first.save()
    second.telegram_chat_id = ""
    second.save()
    first.refresh_from_db()
    second.refresh_from_db()
    assert first.telegram_chat_id is None
    assert second.telegram_chat_id is None


def test_create_superuser_rejects_invalid_staff() -> None:
    """create_superuser с is_staff=False поднимает ValueError."""
    with pytest.raises(ValueError, match="is_staff"):
        User.objects.create_superuser(
            email="bad@example.com",
            password="StrongPass123!",
            is_staff=False,
        )
