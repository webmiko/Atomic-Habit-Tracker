# Фронтенд

Статический UI без React/Vue: **Bootstrap 5.3** (CDN) + vanilla JS (`fetch`).

## Структура

```text
frontend/
  register.html
  login.html
  cabinet.html          # shell: navbar + вкладки
  css/custom.css
  js/config.js          # API_BASE_URL (:5500 → :8000, иначе same-origin)
  js/api.js             # fetch + JWT, refresh при 401
  js/auth.js            # login, refresh, logout (localStorage)
  js/cabinet.js         # hash-роутинг, escapeHtml для полей API
```

## Вкладки кабинета

| Hash | Экран | API |
|------|-------|-----|
| `#my` | мои привычки, CRUD, toggle публичности | `/api/habits/` |
| `#community` | лента чужих публичных, copy | `/api/habits/public/` |
| `#templates` | каталог 16 пар | `/api/habits/templates/` |
| `#settings` | профиль, оповещения, код Telegram | `/api/users/me/` |

## Базовый URL API

`config.js`: при открытии с Live Server (`:5500`) запросы идут на `http://127.0.0.1:8000`;
при раздаче через Django/WhiteNoise — `window.location.origin` (один порт для UI и API).

## JWT в браузере

После `POST /api/token/` — `access` и `refresh` в `localStorage`.

`api.js` добавляет заголовок `Authorization: Bearer ...`. При 401 — попытка refresh
(`auth.js`), затем повтор запроса или редирект на `login.html`.

Поля с API в карточках экранируются через `escapeHtml()` (защита от XSS при `innerHTML`).

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
