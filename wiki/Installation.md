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
git checkout develop          # или актуальная feature-ветка
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

Имена management-команд уточняются при реализации этапа Telegram.

## Фронтенд

Папка `frontend/`. Локально — Live Server на порту **5500** (должен быть в `CORS_ALLOWED_ORIGINS`).
См. [Frontend.md](Frontend.md).

## Интерпретатор IDE

**Cursor / VS Code:** `Python: Select Interpreter` → `./.venv/bin/python`.
