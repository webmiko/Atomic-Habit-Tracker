# API

Базовый URL: `http://127.0.0.1:8000`. Интерактивная схема: `/swagger/`, `/redoc/`.

Авторизация: заголовок `Authorization: Bearer <access_token>` (кроме register и token).

## Аутентификация

| Метод | URL | Права | Тело / ответ |
|-------|-----|-------|--------------|
| POST | `/api/users/register/` | AllowAny | email, password → 201 |
| POST | `/api/token/` | AllowAny | email, password → access, refresh |
| POST | `/api/token/refresh/` | AllowAny | refresh → новый access |

## Профиль

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/users/me/` | профиль, счётчики привычек, флаги notify |
| PATCH | `/api/users/me/` | `public_display_name`, notify, без смены пароля в MVP |

## Мои привычки

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/habits/` | список своих, пагинация 5 |
| POST | `/api/habits/` | создать, `user` подставляется автоматически |
| GET | `/api/habits/{id}/` | одна своя |
| PATCH | `/api/habits/{id}/` | изменить свою, в т.ч. `is_public` |
| DELETE | `/api/habits/{id}/` | удалить свою |

Чужая по id → **404**.

## Публичные привычки

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/habits/public/` | лента `is_public=True`, пагинация 5 |
| GET | `/api/habits/public/{id}/` | карточка; только публичные |
| POST | `/api/habits/public/{id}/copy/` | копия у текущего user, `is_public=False` |

PATCH/DELETE на public-маршруте → **404**.

**Public JSON:** action, place, time, duration, periodicity, reward/related_action,
`author_name`, `formula`. Без email, user id, chat_id.

## Шаблоны

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/habits/templates/` | каталог (read-only) |
| POST | `/api/habits/from-template/{id}/` | создать привычку(и) из шаблона |

## Telegram

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/api/users/telegram/link/` | выдать одноразовый код привязки |

## Пример: вход и список

```bash
# Токен
curl -s -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secret"}'

# Список привычек
curl -s http://127.0.0.1:8000/api/habits/ \
  -H "Authorization: Bearer <access>"
```

## Коды ответов

| Код | Когда |
|-----|-------|
| 200 | успешное чтение / обновление |
| 201 | создание |
| 400 | ошибка валидации |
| 401 | нет или просрочен JWT |
| 404 | объект не найден или нет прав (чужая привычка) |
