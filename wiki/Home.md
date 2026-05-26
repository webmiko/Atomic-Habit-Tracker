# Wiki — Atomic Habit Tracker

Документация проекта в репозитории. Краткий обзор — в [README](../README.md).

## Содержание

| Раздел | Описание |
|--------|----------|
| [Установка](Installation.md) | Poetry, PostgreSQL, первый запуск |
| [Переменные окружения](Environment-Variables.md) | `.env` и `.env.template` |
| [Архитектура](Architecture.md) | компоненты, блок-схемы алгоритмов |
| [Модели и валидаторы](Models-and-Validators.md) | User, Habit, HabitTemplate, 6 правил |
| [API](API.md) | эндпоинты, права, пагинация, примеры |
| [Оповещения](Notifications.md) | Celery Beat, email, Telegram |
| [Telegram-бот](Telegram-Bot.md) | токен, привязка chat_id, команды |
| [Фронтенд](Frontend.md) | Bootstrap 5.3, кабинет, CORS |
| [Тестирование](Testing.md) | pytest, coverage ≥80%, `make check` |
| [Git-воркфлоу](Git-Workflow.md) | main, develop, feature-ветки |
| [Чеклист сдачи](Course-Checklist.md) | 13 критериев курса |

## Стек

Django 6 · DRF · SimpleJWT · PostgreSQL · Celery · Redis · drf-yasg · requests (Telegram) ·
Bootstrap 5.3 (статический фронт).

## Быстрые ссылки

| URL | Назначение |
|-----|------------|
| `http://127.0.0.1:8000/login.html` | вход (Gunicorn / `runserver` + WhiteNoise) |
| `http://127.0.0.1:8000/cabinet.html` | кабинет |
| `http://127.0.0.1:8000/admin/` | Django Admin |
| `http://127.0.0.1:8000/swagger/` | Swagger UI |
| `http://127.0.0.1:8000/redoc/` | ReDoc |
| `http://127.0.0.1:5500/login.html` | фронт отдельно (Live Server, CORS на :8000) |

Docker Compose: один порт **8000** для API и статики — см. [README § Деплой](../README.md).
