# Архитектура

Полные блок-схемы — в [README § Логика приложения](../README.md#логика-приложения-блок-схемы).
Здесь — текстовое описание слоёв.

## Слои

```text
┌─────────────┐     JWT + JSON      ┌──────────────────────────┐
│  frontend/  │ ──────────────────► │  Gunicorn + Django + DRF │
│  Bootstrap  │ ◄────────────────── │  WhiteNoise (статика)    │
└─────────────┘                     └────────┬─────────────────┘
                                           │
                    ┌──────────────────────┼──────────────────────┐
                    ▼                      ▼                      ▼
             ┌────────────┐        ┌────────────┐        ┌────────────┐
             │ PostgreSQL │        │   Redis    │        │  Telegram  │
             │ User Habit │        │   broker   │        │  Bot API   │
             └────────────┘        └─────┬──────┘        └────────────┘
                                         │
                                   Celery Beat
                                   send_habit_reminders
                                         │
                                   email (send_mail)
```

## Приложения Django

| App | Ответственность |
|-----|----------------|
| `config` | settings, urls, celery, WSGI |
| `users` | User, регистрация, JWT, `/me/`, сервисы email и Telegram |
| `habits` | Habit, HabitTemplate, API, валидаторы, Celery-задачи |

## Ключевые алгоритмы

| Алгоритм | Где | Документ |
|----------|-----|----------|
| Права и 404 чужих | ViewSet + `IsOwner` | [API.md](API.md) |
| Валидация привычки | `habits/validators.py` | [Models-and-Validators.md](Models-and-Validators.md) |
| Публичная лента + copy | `HabitPublicViewSet` | [API.md](API.md) |
| Шаблон → привычка | `from-template`, `atomic()` | [Models-and-Validators.md](Models-and-Validators.md) |
| Напоминания | Celery Beat + задача | [Notifications.md](Notifications.md) |
| Привязка Telegram | код + бот `/link` | [Telegram-Bot.md](Telegram-Bot.md) |

## Безопасность (кратко)

- Queryset личных привычек: только `request.user`; поле `user` в POST игнорируется (read-only).
- Чужой объект по id → **404**, не 403.
- Public serializer без email, `user_id`, `telegram_chat_id`.
- Секреты только из `os.getenv` / `.env`; `SECRET_KEY` обязателен при `DEBUG=False`.
- `ENABLE_PROD_SECURITY=True` — HTTPS-куки и редирект (prod).
- Telegram: не логировать traceback с URL, содержащим bot token.
- Фронт: `escapeHtml()` для пользовательских строк в `cabinet.js`.
