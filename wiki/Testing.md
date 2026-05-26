# Тестирование

## Запуск

```bash
poetry run pytest
poetry run pytest --cov=config --cov=users --cov=habits --cov-report=term-missing
```

Цель сдачи: покрытие **≥ 80%** по `config`, `users`, `habits`.

## Makefile

```bash
make test       # pytest + cov (config, users, habits), fail-under 80%
make check      # ruff + format + mypy + test
```

В `pyproject.toml` и `Makefile` источники покрытия: `config`, `users`, `habits`.

## Типы тестов

| Область | Что проверять |
|---------|----------------|
| Auth | register, token, 401 без JWT |
| Habit CRUD | только свои; чужой id → 404 |
| Валидаторы | по одному негативному кейсу на правило |
| Public | list без PII; copy создаёт новую запись |
| Pagination | `count`, `results` ≤ 5, вторая страница |
| Celery | eager + `mail.outbox`, mock Telegram |
| Swagger | `GET /swagger.json` — ключевые paths |
| Security | `tests/test_security.py`: SECRET_KEY, CORS, подмена `user`, пароль не в ответе |

## Celery в тестах

`tests/conftest.py`:

```python
@pytest.fixture(autouse=True)
def _celery_eager(settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
```

Для демо на сдаче — отдельно запустить worker и beat (см. [Notifications.md](Notifications.md)).

## Линтеры

```bash
poetry run ruff check .
poetry run ruff format .
poetry run mypy .
```

Лимит строки: **119** символов.

## Отчёт покрытия

После `make test` смотрите вывод в терминале; файл `coverage.txt` создаётся локально
и не предназначен для коммита.
