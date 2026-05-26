# Модели и валидаторы

## User (`users/models.py`)

Расширение `AbstractUser`, вход по **email**.

| Поле | Тип | Назначение |
|------|-----|------------|
| `email` | unique | логин |
| `public_display_name` | CharField | имя в публичной ленте |
| `notify_by_email` | bool, default True | канал email |
| `notify_by_telegram` | bool, default False | канал Telegram |
| `telegram_chat_id` | CharField, null, unique | после привязки бота; пустая строка → NULL при save |

`telegram_chat_id` не отдаётся в REST API (в `/me/` только `telegram_linked`).

## Habit (`habits/models.py`)

| Поле | Ограничение |
|------|-------------|
| `user` | FK → User, владелец |
| `place`, `action` | текст по ТЗ |
| `time` | TimeField — время напоминания |
| `duration` | секунды, **≤ 120** |
| `periodicity` | дни, **1–7**, default 1 |
| `is_pleasant` | приятная / полезная |
| `related_habit` | self FK, только pleasant, `PROTECT` |
| `reward` | текст награды |
| `is_public` | видна в ленте сообщества |
| `last_notified_at` | DateTime, для Celery |

`clean()` дублирует правила сериализатора.

## HabitTemplate

Каталог готовых привычек (без `user`, `is_public`, `last_notified_at`).

Дополнительно: `category`, `slug`, `tagline`, `pair_group`, `sort_order`, `is_featured`,
`suggested_related_template` (FK на pleasant-шаблон).

Seed: 13 pleasant + 16 useful + 16 пар.

## Шесть правил валидации

Реализация: `habits/validators.py` + `HabitSerializer.validate()`.

| # | Правило | Ошибка |
|---|---------|--------|
| 1 | Нельзя одновременно `related_habit` и `reward` | 400 |
| 2 | `duration` ≤ 120 | 400 |
| 3 | `related_habit` только pleasant **того же** user | 400 |
| 4 | У pleasant: пустые `related_habit` и `reward` | 400 |
| 5 | `periodicity` в диапазоне 1–7 | 400 |
| 6 | У useful: нужен `reward` **или** `related_habit` (пробелы в reward не считаются) | 400 |

## Удаление pleasant с связью

`related_habit` → `on_delete=PROTECT`: нельзя удалить приятную привычку, на которую
ссылается полезная.

## Пагинация списков

`HabitPageNumberPagination`: `page_size=5`, без смены размера страницы.

Ответ: `count`, `next`, `previous`, `results` (не `limit`/`offset`).
