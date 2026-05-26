"""Smoke-тесты конфигурации Django и подключения к БД."""

import pytest
from django.core.management import call_command


@pytest.mark.django_db
def test_migrate_applies() -> None:
    """Проверяет, что все миграции накатываются без ошибок."""
    call_command("migrate", verbosity=0, interactive=False)


def test_django_check_passes() -> None:
    """Проверяет, что ``manage.py check`` не сообщает о проблемах."""
    call_command("check")
