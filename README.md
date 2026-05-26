# Atomic Habit Tracker

Backend и API для трекера привычек по принципам *Atomic Habits*: полезные и приятные
привычки, связки, публичная лента, напоминания в Telegram и по email.

**Стек:** Django 6, DRF, SimpleJWT, PostgreSQL, Celery + Redis, drf-yasg, Bootstrap 5.3 (фронт).

Репозиторий: [github.com/webmiko/Atomic-Habit-Tracker](https://github.com/webmiko/Atomic-Habit-Tracker)

---

## Логика приложения (блок-схемы)

Ниже — **алгоритмы и взаимодействия** системы, а не порядок разработки.
Прямоугольник — процесс · ромб — условие · цилиндр — хранилище · параллелограмм — ввод/вывод.

### 1. Компоненты и потоки данных

```mermaid
flowchart LR
  subgraph CLIENT["Клиент"]
    FE["frontend/<br/>fetch + JWT"]
  end

  subgraph API["Django + DRF"]
    AUTH["JWTAuthentication"]
    REG["register / token"]
    ME["users/me"]
    HAB["HabitViewSet<br/>CRUD · owner"]
    PUB["HabitPublicViewSet<br/>read · copy"]
    TPL["templates /<br/>from-template"]
    VAL["habits/validators"]
  end

  subgraph STORE["Хранение"]
    PG[("PostgreSQL<br/>User · Habit · Template")]
  end

  subgraph ASYNC["Фоновые задачи"]
    BEAT["Celery Beat<br/>каждую минуту"]
    TASK["send_habit_reminders"]
    REDIS[("Redis broker")]
  end

  subgraph OUT["Каналы оповещений"]
    MAIL["send_mail<br/>email"]
    TGAPI["requests →<br/>Telegram Bot API"]
  end

  BOT["Telegram-бот<br/>/link код"]

  FE -->|HTTPS + Bearer| AUTH
  AUTH --> HAB & PUB & ME & TPL
  REG & ME --> PG
  HAB --> VAL --> PG
  PUB --> PG
  TPL --> PG
  BEAT --> REDIS --> TASK
  TASK --> PG
  TASK --> MAIL & TGAPI
  FE -->|код привязки| ME
  BOT -->|chat_id| PG
```

### 2. Доступ к привычке (API)

```mermaid
flowchart TB
  REQ["HTTP-запрос с JWT"]
  REQ --> AUTH_OK{"Токен<br/>валиден?"}
  AUTH_OK -->|нет| E401["401 Unauthorized"]
  AUTH_OK -->|да| ROUTE{"Маршрут?"}

  ROUTE -->|/api/habits/…| OWN["queryset:<br/>user = request.user"]
  OWN --> ACT{"action?"}
  ACT -->|list/create| OK_OWN["200 / 201"]
  ACT -->|retrieve/update/delete| IS_OWNER{"id принадлежит<br/>пользователю?"}
  IS_OWNER -->|да| OK_OWN
  IS_OWNER -->|нет| E404A["404 Not Found"]

  ROUTE -->|/api/habits/public/…| PUB_Q["queryset:<br/>is_public = True"]
  PUB_Q --> ACTP{"action?"}
  ACTP -->|list/retrieve| OK_PUB["200 · без PII владельца"]
  ACTP -->|copy| COPY["создать Habit<br/>у request.user"]
  COPY --> OK_COPY["201 · is_public=False"]
  ACTP -->|patch/delete| E404B["404 · запрещено"]

  ROUTE -->|register / token| OPEN["AllowAny"]
  OPEN --> OK_OPEN["201 / 200 + JWT"]
```

### 3. Алгоритм: сохранение привычки (валидация)

```mermaid
flowchart TB
  IN["POST / PATCH HabitSerializer"]
  IN --> V1{"related_habit И reward<br/>одновременно?"}
  V1 -->|да| ERR1["400 · только одно"]
  V1 -->|нет| V2{"duration > 120?"}
  V2 -->|да| ERR2["400"]
  V2 -->|нет| V3{"periodicity<br/>в 1…7?"}
  V3 -->|нет| ERR3["400"]
  V3 -->|да| KIND{"is_pleasant?"}

  KIND -->|да| V4{"reward или related<br/>заполнены?"}
  V4 -->|да| ERR4["400 · pleasant пустые"]
  V4 -->|нет| SAVE_P["save pleasant"]

  KIND -->|нет| V5{"есть reward<br/>ИЛИ related?"}
  V5 -->|нет| ERR5["400 · useful нужна награда"]
  V5 -->|да| V6{"related указывает<br/>на pleasant того же user?"}
  V6 -->|нет| ERR6["400"]
  V6 -->|да| SAVE_U["save useful · user=owner"]
  SAVE_P --> DB[("PostgreSQL")]
  SAVE_U --> DB
```

### 4. Алгоритм: привычка из шаблона (`from-template`)

```mermaid
flowchart TB
  START["POST /from-template/{id}"]
  START --> LOAD["загрузить HabitTemplate"]
  LOAD --> KIND{"is_pleasant<br/>в шаблоне?"}

  KIND -->|да| ONE["одна запись Habit<br/>is_pleasant=True"]
  ONE --> COMMIT

  KIND -->|нет| PAIR{"есть<br/>suggested_related?"}
  PAIR -->|да| TWO["atomic:<br/>1) pleasant-копия<br/>2) useful + FK related"]
  PAIR -->|нет| REW["одна useful<br/>только reward"]
  TWO --> COMMIT
  REW --> COMMIT

  COMMIT["transaction.commit"] --> OUT["201 · привычки у request.user"]
  COMMIT -.->|ошибка валидатора| ROLL["rollback · 400"]
```

### 5. Алгоритм: напоминания (Celery Beat)

```mermaid
flowchart TB
  TICK["Beat: каждую минуту"]
  TICK --> TASK["send_habit_reminders"]
  TASK --> NOW["now = localtime(TIME_ZONE)"]
  NOW --> LOOP["для каждой Habit<br/>is_pleasant=False"]

  LOOP --> T1{"habit.time в<br/>текущей минуте?"}
  T1 -->|нет| SKIP["пропуск"]
  T1 -->|да| T2{"прошло ≥ periodicity<br/>дней с last_notified_at?"}
  T2 -->|нет| SKIP
  T2 -->|да| USER["загрузить User"]

  USER --> CH1{"notify_by_email?"}
  CH1 -->|да| MAIL["send_mail"]
  CH1 -->|нет| CH2
  MAIL --> CH2{"notify_by_telegram<br/>и chat_id?"}
  CH2 -->|да| TG["telegram.send_message"]
  CH2 -->|нет| UPD
  TG --> UPD

  UPD{"хотя бы один<br/>канал успешен?"}
  UPD -->|да| STAMP["last_notified_at = now"]
  UPD -->|нет| LOG["logger.exception<br/>без stamp"]
  STAMP --> LOOP
  SKIP --> LOOP
```

Ошибка одного канала **не блокирует** второй; stamp только после успешной отправки.

### 6. Привязка Telegram

```mermaid
flowchart LR
  UI["cabinet #settings<br/>код из API"] --> API["POST /users/telegram/link/"]
  API --> DB1[("сохранить код<br/>TTL 10–15 мин")]
  USER["пользователь в боте<br/>/link КОД"] --> BOT["polling management command"]
  BOT --> DB2[("user.telegram_chat_id")]
  DB1 -.->|совпадение кода| DB2
  DB2 --> TASK
  TASK["send_habit_reminders"] --> TG["Bot API"]
```

---

## Прогресс реализации

| Этап | Статус | Ветка |
|------|--------|-------|
| Окружение, Postgres, зависимости | ✅ | `main` / `develop` |
| Каркас Django | 🔄 | `feature/step_1` |
| API, напоминания, фронт | ⬜ | `feature/step_N` |

`main` ← `develop` ← `feature/step_N` (PR после каждого этапа).

---

## Требования

- Python **3.14+**
- [Poetry](https://python-poetry.org/) 2.x
- **PostgreSQL** 14+
- **Redis** (с шага 7 — Celery)

---

## Быстрый старт

```bash
git clone https://github.com/webmiko/Atomic-Habit-Tracker.git
cd Atomic-Habit-Tracker
git checkout feature/step_1   # или актуальная feature-ветка

poetry install
cp .env.template .env         # заполните DB_* и позже TELEGRAM_BOT_TOKEN
```

### PostgreSQL

Пример (подставьте свои имя БД и пользователя):

```sql
CREATE DATABASE atomic_habits;
```

В `.env`: `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.

После шага 1:

```bash
poetry run python manage.py migrate
poetry run python manage.py runserver
```

### Переменные окружения

Шаблон для копирования — **`.env.template`** (в репозитории). Локальный **`.env`**
не коммитится; создайте его из шаблона.

| Группа | Назначение |
|--------|------------|
| `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` | Django |
| `DB_*` | PostgreSQL |
| `CELERY_*` | Redis |
| `TELEGRAM_BOT_TOKEN` | бот |
| `EMAIL_*` | по умолчанию console backend для отладки |

---

## Качество кода

```bash
poetry run ruff check .
poetry run ruff format .
poetry run mypy .
poetry run pytest
poetry run pytest --cov=config --cov=users --cov=habits --cov-report=term-missing
```

Лимит строки в коде: **119** символов (Ruff).

| Команда | Назначение |
|---------|------------|
| `make install` | `poetry install` |
| `make lint` / `format` / `typecheck` / `test` | см. `Makefile` |
| `make check` | lint + format + mypy + test |

---

## Структура репозитория

**Целевая** (после шага 1):

```text
├── config/              # settings, urls, celery
├── users/               # User, JWT, Telegram-сервис
├── habits/              # Habit, API, валидаторы, задачи
├── tests/
├── frontend/            # HTML + Bootstrap 5.3
├── manage.py
├── pyproject.toml
├── poetry.lock
├── .env.template
└── README.md
```

Сейчас (до завершения шага 1): временный каркас `src/atomic_habit_tracker/` и `main.py`.

---

## API

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/api/users/register/` | регистрация |
| POST | `/api/token/`, `/api/token/refresh/` | JWT |
| GET/PATCH | `/api/users/me/` | профиль и настройки |
| GET/POST | `/api/habits/` | мои привычки |
| GET/PATCH/DELETE | `/api/habits/{id}/` | одна привычка |
| GET | `/api/habits/public/` | публичная лента |
| POST | `/api/habits/public/{id}/copy/` | копия к себе |
| GET | `/api/habits/templates/` | каталог шаблонов |

Документация: `/swagger/`, `/redoc/`.

---

## Зависимости (Poetry)

| Пакет | Назначение |
|-------|------------|
| django, djangorestframework | API |
| djangorestframework-simplejwt | JWT |
| django-cors-headers, drf-yasg | CORS, OpenAPI |
| celery, redis, django-celery-beat | периодические задачи |
| psycopg2-binary | PostgreSQL |
| requests | Telegram Bot API |
| python-dotenv | переменные из `.env` |

Dev: pytest, pytest-django, pytest-cov, ruff, mypy.

---

## Критерии сдачи курса (кратко)

| # | Тема |
|---|------|
| 1 | CORS |
| 2 | Telegram / email по расписанию |
| 3 | Пагинация (`count`, `next`, `previous`, `results`, ≤5) |
| 4 | `.env` + `.env.template` |
| 5–7 | Модели, API, валидаторы |
| 8 | JWT |
| 9 | Celery без ошибок в runtime |
| 10 | Покрытие тестами ≥80% |
| 11 | PEP 8 (Ruff) |
| 12–13 | Зависимости в `pyproject.toml`, Swagger |

Подробная документация: **[wiki/Home.md](wiki/Home.md)** (установка, API, Celery, чеклист сдачи).
