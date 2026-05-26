# Atomic Habit Tracker

Трекер привычек (Django + DRF + Celery + PostgreSQL). Этап 0: Poetry, зависимости, `.env`.

## Требования

- Python **3.14+**
- [Poetry](https://python-poetry.org/) 2.x
- **PostgreSQL** 14+ (локально или Docker)
- **Redis** (для Celery; позже, на этапе напоминаний)

## Быстрый старт

```bash
cd atomic-habit-tracker

# Зависимости (.venv в корне)
poetry install

# Переменные окружения (если нет .env)
cp .env.template .env
# Отредактируйте .env: DB_PASSWORD, позже TELEGRAM_BOT_TOKEN
```

### PostgreSQL

Создайте базу и пользователя (пример; подставьте свой пароль):

```sql
CREATE USER atomic_habits_user WITH PASSWORD 'your-password';
CREATE DATABASE atomic_habits OWNER atomic_habits_user;
```

В `.env` укажите `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.

Проверка подключения (после появления `manage.py`):

```bash
poetry run python manage.py check --database default
```

### Заглушка (до Django)

```bash
poetry run python main.py
```

## Интерпретатор в Cursor / VS Code

После `poetry install` выберите интерпретатор:

**Command Palette** → `Python: Select Interpreter` → `./.venv/bin/python`

Локальные настройки (не в Git): `.vscode/settings.json` с путём к `.venv`.

## Качество кода

| Команда | Назначение |
|---------|------------|
| `poetry run ruff check .` | Линт |
| `poetry run ruff format .` | Форматирование |
| `poetry run mypy .` | Типы |
| `poetry run pytest` | Тесты |
| `poetry run pytest --cov=src --cov-report=term-missing` | Покрытие |

Лимит строки: **119** символов (Ruff).

## Зависимости (Poetry)

| Пакет | Назначение |
|-------|------------|
| django, djangorestframework | API |
| djangorestframework-simplejwt | JWT |
| django-cors-headers, drf-yasg | CORS, Swagger |
| celery, redis, django-celery-beat | напоминания |
| psycopg2-binary | PostgreSQL |
| requests | Telegram Bot API |
| python-dotenv | `.env` |

Dev: pytest, pytest-django, pytest-cov, ruff, mypy.

## Структура

```
├── src/atomic_habit_tracker/   # временный каркас (снимется при Django)
├── tests/
├── main.py
├── pyproject.toml, poetry.lock
├── .env.template               # шаблон для Git (рубрика)
├── .env                        # локально, не в Git
└── poetry.toml                 # venv → .venv/
```


## GitHub

Репозиторий ещё не создан — выполните один раз:

```bash
git init
git add .
git commit -m "chore: инициализация проекта Poetry и инструментов качества"

# Создать репозиторий на GitHub (имя на ваш выбор)
gh repo create atomic-habit-tracker --private --source=. --remote=origin --push
```

Без `gh`: создайте пустой репозиторий на GitHub и выполните:

```bash
git remote add origin git@github.com:<USER>/atomic-habit-tracker.git
git branch -M main
git push -u origin main
```

## Дальше

1. Итерация 1: `django-admin startproject`, apps `users` / `habits`, `load_dotenv` + Postgres в settings
2. В `.env` добавить `TELEGRAM_BOT_TOKEN` от [@BotFather](https://t.me/BotFather)
