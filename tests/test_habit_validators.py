"""Тесты шести бизнес-правил валидации Habit."""

from datetime import time

import pytest
from django.core.exceptions import ValidationError
from rest_framework import serializers as drf_serializers

from habits.models import Habit
from habits.serializers import HabitSerializer
from habits.validators import (
    validate_duration_seconds,
    validate_not_both_related_and_reward,
    validate_periodicity_days,
    validate_pleasant_habit_fields,
    validate_related_habit_owner,
    validate_useful_habit_has_reward,
)
from users.models import User


@pytest.fixture
def user(db: None) -> User:
    """Создаёт пользователя для привязки привычек."""
    return User.objects.create_user(email="habit@example.com", password="StrongPass123!")


@pytest.fixture
def pleasant_habit(user: User) -> Habit:
    """Создаёт приятную привычку без награды."""
    return Habit.objects.create(
        user=user,
        place="Кухня",
        time=time(8, 0),
        action="Выпить воду",
        is_pleasant=True,
        duration=30,
        periodicity=1,
    )


def test_rule1_not_both_related_and_reward() -> None:
    """Правило 1: нельзя указать related_habit и reward вместе."""
    with pytest.raises(ValidationError):
        validate_not_both_related_and_reward(related_habit=object(), reward="чай")


def test_rule2_duration_max_120() -> None:
    """Правило 2: duration не больше 120 секунд."""
    with pytest.raises(ValidationError):
        validate_duration_seconds(121)


def test_rule3_related_must_be_pleasant_same_user(user: User, pleasant_habit: Habit) -> None:
    """Правило 3: related только pleasant того же пользователя."""
    other = User.objects.create_user(email="other@example.com", password="StrongPass123!")
    foreign_pleasant = Habit.objects.create(
        user=other,
        place="Дом",
        time=time(9, 0),
        action="Чужая приятная",
        is_pleasant=True,
        duration=20,
        periodicity=1,
    )
    with pytest.raises(ValidationError):
        validate_related_habit_owner(foreign_pleasant, user)

    useful_as_related = Habit.objects.create(
        user=user,
        place="Дом",
        time=time(9, 30),
        action="Полезная без pleasant",
        is_pleasant=False,
        reward="чай",
        duration=60,
        periodicity=1,
    )
    with pytest.raises(ValidationError):
        validate_related_habit_owner(useful_as_related, user)


def test_rule4_pleasant_without_reward_fields() -> None:
    """Правило 4: у pleasant пустые related и reward."""
    with pytest.raises(ValidationError):
        validate_pleasant_habit_fields(True, None, "награда")


def test_rule5_periodicity_range() -> None:
    """Правило 5: periodicity от 1 до 7."""
    with pytest.raises(ValidationError):
        validate_periodicity_days(0)
    with pytest.raises(ValidationError):
        validate_periodicity_days(8)


def test_rule6_useful_needs_reward_or_related() -> None:
    """Правило 6: полезной нужна награда или related_habit."""
    with pytest.raises(ValidationError):
        validate_useful_habit_has_reward(False, None, "")


@pytest.mark.django_db
def test_model_clean_blocks_invalid_useful(user: User) -> None:
    """Habit.full_clean() отклоняет полезную привычку без награды."""
    habit = Habit(
        user=user,
        place="Стол",
        time=time(12, 0),
        action="Работа",
        is_pleasant=False,
        duration=60,
        periodicity=1,
    )
    with pytest.raises(ValidationError):
        habit.full_clean()


@pytest.mark.django_db
def test_serializer_validates_useful_with_related(user: User, pleasant_habit: Habit) -> None:
    """HabitSerializer принимает полезную привычку со связью."""
    serializer = HabitSerializer(
        data={
            "place": "Стол",
            "time": "12:00:00",
            "action": "Сделать задачу",
            "is_pleasant": False,
            "related_habit": pleasant_habit.pk,
            "duration": 90,
            "periodicity": 2,
            "is_public": False,
        },
        context={"request": type("R", (), {"user": user})()},
    )
    assert serializer.is_valid(), serializer.errors


@pytest.mark.django_db
def test_delete_pleasant_with_link_raises_protected(user: User, pleasant_habit: Habit) -> None:
    """Удаление pleasant с PROTECT при связанной useful запрещено."""
    Habit.objects.create(
        user=user,
        place="Стол",
        time=time(12, 0),
        action="Полезная",
        is_pleasant=False,
        related_habit=pleasant_habit,
        duration=60,
        periodicity=1,
    )
    from django.db.models import ProtectedError

    with pytest.raises(ProtectedError):
        pleasant_habit.delete()


@pytest.mark.django_db
def test_serializer_rejects_both_reward_types(user: User, pleasant_habit: Habit) -> None:
    """Сериализатор отклоняет related и reward одновременно."""
    serializer = HabitSerializer(
        data={
            "place": "Стол",
            "time": "12:00:00",
            "action": "Задача",
            "is_pleasant": False,
            "related_habit": pleasant_habit.pk,
            "reward": "чай",
            "duration": 60,
            "periodicity": 1,
        },
        context={"request": type("R", (), {"user": user})()},
    )
    assert not serializer.is_valid()
    with pytest.raises(drf_serializers.ValidationError):
        serializer.is_valid(raise_exception=True)
