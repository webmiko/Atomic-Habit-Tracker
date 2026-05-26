# Git-воркфлоу

## Ветки

```text
main          стабильные релизы, сдача курса
  └── develop     интеграция завершённых этапов
        └── feature/step_N   разработка одного этапа
```

| Ветка | Когда использовать |
|-------|-------------------|
| `main` | после проверки на `develop`, теги релиза |
| `develop` | merge feature после review |
| `feature/step_N` | разработка в отдельной ветке |

Имена feature-веток: `feature/step_<номер>`.

## Типичный цикл

```bash
git checkout develop
git pull origin develop
git checkout -b feature/step_2

# работа, коммиты
git push -u origin feature/step_2

# Pull Request: feature/step_2 → develop
# после merge:
git checkout develop
git pull origin develop

# релиз на main (по готовности):
git checkout main
git merge develop
git push origin main
```

## Что не коммитить

- `.env` (секреты и токены)
- `.venv/`, `__pycache__/`, `.pytest_cache/`, `htmlcov/`, `coverage.txt`



## Текущее состояние

| Ветка | Содержимое |
|-------|------------|
| `feature/step_1` | полный MVP: habits API, шаблоны, Celery, Telegram, фронт, Docker |
| `develop` / `main` | merge по мере сдачи курса |

После merge `feature/step_1` → `develop` новые задачи — ветки `feature/step_N`.
