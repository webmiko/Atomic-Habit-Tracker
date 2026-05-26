# Переменные окружения

Секреты только в **`.env`** (не в Git). Шаблон для копирования — **`.env.template`** (в репозитории).

```bash
cp .env.template .env
```

## Django

| Переменная | Обязательно | Описание |
|------------|-------------|----------|
| `SECRET_KEY` | да | ключ Django; в prod — случайная строка |
| `DEBUG` | да | `True` локально, `False` на проде |
| `ALLOWED_HOSTS` | да | через запятую: `localhost,127.0.0.1,testserver` |
| `TIME_ZONE` | да | например `Europe/Moscow` |

## PostgreSQL

| Переменная | По умолчанию | Описание |
|------------|--------------|----------|
| `DB_NAME` | — | имя БД, например `atomic_habits` |
| `DB_USER` | — | пользователь PostgreSQL |
| `DB_PASSWORD` | пусто | пароль (локально может быть пустым) |
| `DB_HOST` | `localhost` | хост |
| `DB_PORT` | `5432` | порт |

## CORS и фронт

| Переменная | Пример |
|------------|--------|
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5500,http://127.0.0.1:5500` |
| `FRONTEND_URL` | `http://localhost:5500` |

## Celery

| Переменная | Пример |
|------------|--------|
| `CELERY_BROKER_URL` | `redis://localhost:6379/0` |
| `CELERY_RESULT_BACKEND` | `redis://localhost:6379/0` |

## Telegram

| Переменная | Описание |
|------------|----------|
| `TELEGRAM_BOT_TOKEN` | токен от [@BotFather](https://t.me/BotFather) |

Не логировать URL с токеном; не отдавать токен в API-ответах.

## Email

**Отладка (по умолчанию в шаблоне):**

```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@localhost
```

Письма выводятся в консоль `runserver` / worker.

**Яндекс Почта (SMTP)** — раскомментировать блок в `.env.template`:

- `smtp.yandex.ru`, порт `465`, `EMAIL_USE_SSL=True`
- пароль приложения: [id.yandex.ru/security/app-passwords](https://id.yandex.ru/security/app-passwords)

## JWT (опционально)

| Переменная | Назначение |
|------------|------------|
| `JWT_ACCESS_MINUTES` | время жизни access-токена |
| `JWT_REFRESH_DAYS` | время жизни refresh-токена |

Если не заданы — используются значения по умолчанию SimpleJWT в `settings`.
