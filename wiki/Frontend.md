# Фронтенд

Статический UI без React/Vue: **Bootstrap 5.3** (CDN) + vanilla JS (`fetch`).

## Структура

```text
frontend/
  register.html
  login.html
  cabinet.html          # shell: navbar + вкладки
  css/custom.css
  js/api.js             # base URL, Authorization
  js/auth.js            # login, refresh, logout
  js/cabinet.js         # hash-роутинг
```

## Вкладки кабинета

| Hash | Экран | API |
|------|-------|-----|
| `#my` | мои привычки, CRUD, toggle публичности | `/api/habits/` |
| `#community` | лента чужих публичных, copy | `/api/habits/public/` |
| `#templates` | каталог 16 пар | `/api/habits/templates/` |
| `#settings` | профиль, оповещения, код Telegram | `/api/users/me/` |

## JWT в браузере

После `POST /api/token/` — `access` и `refresh` в `localStorage`.

`api.js` добавляет заголовок `Authorization: Bearer ...`. При 401 — попытка refresh
(`auth.js`), затем повтор запроса или редирект на `login.html`.

## CORS

Backend читает `CORS_ALLOWED_ORIGINS` из `.env`. Для Live Server:

```env
CORS_ALLOWED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
```

Запуск фронта: VS Code Live Server или `python -m http.server 5500` из `frontend/`.

## Сценарий проверки

1. Регистрация → вход.
2. Создать привычку в «Мои», включить «публичная».
3. Второй пользователь видит её в «Сообщество», копирует к себе.
4. В «Настройки» — код Telegram, привязка бота.
5. Дождаться напоминания (Celery) — письмо в консоль или TG.

## Дизайн

- Mobile-first, `container` / `row` / `col`.
- Карточка: action, place, time, badge полезная/приятная.
- Акцент success (`#198754`).
