# Чеклист сдачи курса

13 критериев оценки. Отмечайте `[x]` перед сдачей.

## Прогресс

```text
[░░░░░░░░░░░░░░░░░░░░]  0/13
```

## Критерии

| № | Критерий | Как проверить | Статус |
|---|----------|---------------|--------|
| 1 | CORS | OPTIONS/GET с фронта `:5500`; origins в settings | [ ] |
| 2 | Напоминания по расписанию | worker + beat; письмо в консоль или TG | [ ] |
| 3 | Пагинация | `count`, `next`, `previous`, `results`; ≤5 записей | [ ] |
| 4 | Секреты в `.env` | есть `.env.template` в репо; секретов нет в git | [ ] |
| 5 | Модели по ТЗ | User, Habit; миграции; admin | [ ] |
| 6 | Эндпоинты и права | чужие не edit; public list + copy | [ ] |
| 7 | Валидаторы | 6 правил; тесты API | [ ] |
| 8 | Авторизация | register + JWT; 401 без токена | [ ] |
| 9 | Celery без ошибок | beat 2–3 мин без traceback | [ ] |
| 10 | Покрытие ≥80% | `pytest --cov` | [ ] |
| 11 | PEP 8 | `ruff check` + `ruff format` | [ ] |
| 12 | Зависимости | `poetry install` из lock | [ ] |
| 13 | Документация API | все URL в `/swagger/` | [ ] |

## Swagger — обязательные пути

- [ ] `POST /api/users/register/`
- [ ] `POST /api/token/`, `POST /api/token/refresh/`
- [ ] `GET`, `POST /api/habits/`
- [ ] `GET`, `PATCH`, `DELETE /api/habits/{id}/`
- [ ] `GET /api/habits/public/`
- [ ] `GET/PATCH /api/users/me/` (продукт)
- [ ] `POST /api/habits/public/{id}/copy/` (продукт)
- [ ] `GET /api/habits/templates/`, `POST .../from-template/{id}/`
- [ ] `POST /api/users/telegram/link/`

## Перед демонстрацией

```bash
poetry install
cp .env.template .env   # если ещё нет
poetry run python manage.py migrate
poetry run python manage.py runserver

# отдельные терминалы:
poetry run celery -A config worker -l info
poetry run celery -A config beat -l info
```

Фронт: Live Server `frontend/` на порту 5500.

## Связанные страницы wiki

- [Installation.md](Installation.md)
- [API.md](API.md)
- [Notifications.md](Notifications.md)
- [Testing.md](Testing.md)
