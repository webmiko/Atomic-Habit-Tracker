# Установка

## Требования

- Python **3.14+**
- [Poetry](https://python.poetry.org/) 2.x
- **PostgreSQL** 14+
- **Redis** 5+ (брокер Celery и напоминания)

## Клонирование и ветка

```bash
git clone https://github.com/webmiko/Atomic-Habit-Tracker.git
cd Atomic-Habit-Tracker
git checkout feature/step_1   # или develop / main после merge
poetry install
```

## Переменные окружения

```bash
cp .env.template .env
```

Заполните минимум: `SECRET_KEY`, `DB_*`. Подробнее — [Environment-Variables.md](Environment-Variables.md).

## PostgreSQL

```sql
CREATE DATABASE atomic_habits;
```

На macOS с Homebrew суперпользователь часто совпадает с именем ОС (`whoami`), не `postgres`.

Проверка подключения (после появления `manage.py`):

```bash
poetry run python manage.py check --database default
poetry run python manage.py migrate
```

## Запуск backend

```bash
poetry run python manage.py runserver
```

## Redis и Celery (напоминания)

Терминал 1 — worker:

```bash
poetry run celery -A config worker -l info
```

Терминал 2 — beat:

```bash
poetry run celery -A config beat -l info
```

Терминал 3 — бот (polling):

```bash
poetry run python manage.py run_telegram_bot
```

## Docker Compose (опционально)

Полный стек (PostgreSQL, Redis, web, worker, beat) — в [README § Деплой](../README.md):

```bash
cp .env.template .env
docker compose up --build
```

## Фронтенд

Папка `frontend/`. Варианты:

- **Same-origin:** `runserver` или Docker — `http://127.0.0.1:8000/login.html` (CORS не нужен).
- **Live Server :5500** — origin должен быть в `CORS_ALLOWED_ORIGINS`; API — `http://127.0.0.1:8000`
  (см. `frontend/js/config.js`).

Подробнее — [Frontend.md](Frontend.md).

## Интерпретатор IDE

**Cursor / VS Code:** `Python: Select Interpreter` → `./.venv/bin/python`.
