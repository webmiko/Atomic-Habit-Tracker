"""Общие фикстуры pytest для проекта."""

from pathlib import Path
from typing import Any

import pytest

STATICFILES_DIR = Path(__file__).resolve().parent.parent / "staticfiles"


@pytest.fixture(autouse=True)
def _ensure_staticfiles_dir() -> None:
    """Создаёт каталог staticfiles, чтобы WhiteNoise не предупреждал в тестах."""
    STATICFILES_DIR.mkdir(exist_ok=True)


@pytest.fixture(autouse=True)
def _celery_eager_mode(settings: Any) -> None:
    """Выполняет Celery-задачи синхронно в тестах."""
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True
