"""Seed каталога: 13 pleasant + 16 useful шаблонов."""

from __future__ import annotations

from datetime import datetime, time
from typing import Any

from django.db import migrations

from habits.catalog_seed_data import PLEASANT_TEMPLATES, USEFUL_TEMPLATES


def _parse_time(value: str) -> time:
    """Парсит время HH:MM для поля TimeField."""
    return datetime.strptime(value, "%H:%M").time()


def load_catalog(apps: Any, schema_editor: Any) -> None:
    """Загружает шаблоны pleasant и useful с привязкой пар."""
    habit_template = apps.get_model("habits", "HabitTemplate")
    slug_map: dict[str, Any] = {}

    for index, item in enumerate(PLEASANT_TEMPLATES, start=1):
        template = habit_template(
            slug=item["slug"],
            action=item["action"],
            place=item["place"],
            time=_parse_time(item["time"]),
            duration=item["duration"],
            is_pleasant=True,
            periodicity=1,
            category="calm",
            tagline=item.get("tagline", ""),
            pair_group=item["slug"],
            sort_order=item.get("sort_order", index),
            is_featured=False,
        )
        template.save()
        slug_map[item["slug"]] = template

    for item in USEFUL_TEMPLATES:
        related = None
        related_slug = item.get("related_slug")
        if related_slug:
            related = slug_map[related_slug]

        habit_template.objects.create(
            slug=item["slug"],
            action=item["action"],
            place=item["place"],
            time=_parse_time(item["time"]),
            duration=item["duration"],
            is_pleasant=False,
            periodicity=item["periodicity"],
            category=item["category"],
            tagline=item.get("tagline", ""),
            pair_group=item["pair_group"],
            sort_order=item.get("sort_order", 0),
            is_featured=item.get("is_featured", False),
            suggested_related_template=related,
            reward=item.get("reward", ""),
        )


def unload_catalog(apps: Any, schema_editor: Any) -> None:
    """Удаляет seed-записи каталога."""
    habit_template = apps.get_model("habits", "HabitTemplate")
    slugs = [item["slug"] for item in PLEASANT_TEMPLATES] + [
        item["slug"] for item in USEFUL_TEMPLATES
    ]
    habit_template.objects.filter(slug__in=slugs).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("habits", "0002_habittemplate"),
    ]

    operations = [
        migrations.RunPython(load_catalog, unload_catalog),
    ]
