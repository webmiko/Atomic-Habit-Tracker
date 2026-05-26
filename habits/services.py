"""Сервисы копирования привычек и создания из шаблонов."""

from django.db import transaction

from habits.models import Habit, HabitTemplate
from users.models import User


def _create_habit_from_fields(
    *,
    user: User,
    place: str,
    time: object,
    action: str,
    is_pleasant: bool,
    periodicity: int,
    duration: int,
    related_habit: Habit | None = None,
    reward: str = "",
) -> Habit:
    """Создаёт привычку с валидацией через ``full_clean()``."""
    habit = Habit(
        user=user,
        place=place,
        time=time,
        action=action,
        is_pleasant=is_pleasant,
        periodicity=periodicity,
        duration=duration,
        related_habit=related_habit,
        reward=reward if not related_habit else "",
        is_public=False,
    )
    habit.full_clean()
    habit.save()
    return habit


def copy_habit_to_user(source: Habit, user: User) -> Habit:
    """Копирует публичную привычку в личный кабинет пользователя.

    Для полезной с ``related_habit`` сначала копирует приятную привычку.

    Args:
        source: Исходная публичная привычка.
        user: Владелец копии.

    Returns:
        Созданная полезная или приятная привычка (корневая копия).
    """
    if source.is_pleasant:
        return _create_habit_from_fields(
            user=user,
            place=source.place,
            time=source.time,
            action=source.action,
            is_pleasant=True,
            periodicity=source.periodicity,
            duration=source.duration,
        )

    related: Habit | None = None
    if source.related_habit_id:
        related = copy_habit_to_user(source.related_habit, user)

    return _create_habit_from_fields(
        user=user,
        place=source.place,
        time=source.time,
        action=source.action,
        is_pleasant=False,
        periodicity=source.periodicity,
        duration=source.duration,
        related_habit=related,
        reward=source.reward,
    )


@transaction.atomic
def create_habit_from_template(template: HabitTemplate, user: User) -> Habit:
    """Создаёт привычку(и) пользователя по шаблону каталога.

    Args:
        template: Шаблон из каталога.
        user: Владелец новых привычек.

    Returns:
        Корневая созданная привычка (полезная или приятная).
    """
    if template.is_pleasant:
        return _create_habit_from_fields(
            user=user,
            place=template.place,
            time=template.time,
            action=template.action,
            is_pleasant=True,
            periodicity=template.periodicity,
            duration=template.duration,
        )

    related: Habit | None = None
    if template.suggested_related_template_id:
        related = create_habit_from_template(template.suggested_related_template, user)

    return _create_habit_from_fields(
        user=user,
        place=template.place,
        time=template.time,
        action=template.action,
        is_pleasant=False,
        periodicity=template.periodicity,
        duration=template.duration,
        related_habit=related,
        reward=template.reward,
    )
