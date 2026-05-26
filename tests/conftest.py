"""Общие фикстуры pytest для проекта."""

from typing import Any

import pytest


@pytest.fixture(autouse=True)
def _celery_eager_mode(settings: Any) -> None:
    """Выполняет Celery-задачи синхронно в тестах."""
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True
