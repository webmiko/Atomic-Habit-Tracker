"""Сервисы копирования публичных привычек."""

from habits.models import Habit
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
