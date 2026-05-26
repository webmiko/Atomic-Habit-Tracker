# Оповещения

Напоминания только для **полезных** привычек (`is_pleasant=False`). Приятные — награда
в связке, не отдельное расписание.

## Компоненты

| Компонент | Роль |
|-----------|------|
| `django-celery-beat` | расписание «каждую минуту» |
| `send_habit_reminders` | задача в `habits/tasks.py` |
| `users/services/email.py` | обёртка над `send_mail` |
| `users/services/telegram.py` | `requests` → Bot API |

## Алгоритм задачи

1. `now = timezone.localtime()` (см. `TIME_ZONE` в `.env`).
2. Выбрать привычки, у которых `habit.time` попадает в **текущую минуту**.
3. Проверить **periodicity**: с `last_notified_at` прошло не меньше `periodicity` дней.
4. Для владельца:
   - если `notify_by_email` → `send_mail`;
   - если `notify_by_telegram` и есть `telegram_chat_id` → Telegram.
5. Если **хотя бы один** канал успешен → `last_notified_at = now`.
6. Ошибка одного канала **не отменяет** другой; ошибки — в лог (`logger.exception` для email,
   `logger.error` для Telegram — без traceback с URL, содержащим bot token).

Текст: «Напоминание: {action} в {time} в {place}».

## Запуск для проверки

```bash
# Redis должен быть запущен
redis-server

poetry run celery -A config worker -l info
poetry run celery -A config beat -l info
```

В dev с `EMAIL_BACKEND=console` письмо видно в stdout worker или runserver.

## Тесты

- `CELERY_TASK_ALWAYS_EAGER=True` в `conftest` — синхронный прогон в pytest.
- `mail.outbox` для email.
- `unittest.mock` для `requests.post` (Telegram).

На сдаче курса показать **реальный** worker + beat (критерии 2 и 9).

См. также [Telegram-Bot.md](Telegram-Bot.md).
