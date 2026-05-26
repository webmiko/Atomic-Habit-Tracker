"""Тесты валидации HabitTemplate."""

from datetime import time

import pytest
from django.core.exceptions import ValidationError

from habits.models import HabitTemplate
from habits.validators import run_template_validators


@pytest.mark.django_db
def test_template_clean_rejects_useful_without_reward() -> None:
    """Полезный шаблон без награды не проходит clean()."""
    template = HabitTemplate(
        slug="bad-useful",
        action="Плохой",
        place="Дом",
        time=time(8, 0),
        is_pleasant=False,
        duration=30,
        periodicity=1,
    )
    with pytest.raises(ValidationError):
        template.full_clean()


@pytest.mark.django_db
def test_run_template_validators_rejects_non_pleasant_related() -> None:
    """related-шаблон должен быть приятным."""
    HabitTemplate.objects.create(
        slug="pleasant-tpl",
        action="Приятная",
        place="Дом",
        time=time(8, 0),
        is_pleasant=True,
        duration=20,
        periodicity=1,
    )
    other_useful = HabitTemplate.objects.create(
        slug="other-useful-tpl",
        action="Другая полезная",
        place="Офис",
        time=time(9, 0),
        is_pleasant=False,
        reward="чай",
        duration=60,
        periodicity=1,
    )
    with pytest.raises(ValidationError, match="приятн"):
        run_template_validators(
            is_pleasant=False,
            suggested_related_template=other_useful,
            periodicity=1,
            reward="",
            duration=60,
        )
