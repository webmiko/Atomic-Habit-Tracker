"""Валидаторы бизнес-правил для модели Habit."""

from django.core.exceptions import ValidationError

MAX_DURATION_SECONDS = 120
MIN_PERIODICITY_DAYS = 1
MAX_PERIODICITY_DAYS = 7


def validate_duration_seconds(duration: int | None) -> None:
    """Проверяет, что длительность не превышает двух минут.

    Args:
        duration: Длительность в секундах.

    Raises:
        ValidationError: Если значение больше 120.
    """
    if duration is not None and duration > MAX_DURATION_SECONDS:
        raise ValidationError(f"Длительность не может превышать {MAX_DURATION_SECONDS} секунд.")


def validate_periodicity_days(periodicity: int | None) -> None:
    """Проверяет периодичность в диапазоне 1–7 дней.

    Args:
        periodicity: Интервал напоминаний в днях.

    Raises:
        ValidationError: Если значение вне диапазона.
    """
    if periodicity is None:
        return
    if not MIN_PERIODICITY_DAYS <= periodicity <= MAX_PERIODICITY_DAYS:
        raise ValidationError(
            f"Периодичность должна быть от {MIN_PERIODICITY_DAYS} до {MAX_PERIODICITY_DAYS} дней."
        )


def validate_not_both_related_and_reward(
    related_habit: object | None,
    reward: str | None,
) -> None:
    """Запрещает одновременное указание связанной привычки и текстовой награды.

    Args:
        related_habit: Связанная приятная привычка или None.
        reward: Текст награды.

    Raises:
        ValidationError: Если заданы оба способа награды.
    """
    if related_habit and reward:
        raise ValidationError("Нельзя указывать одновременно связанную привычку и награду.")


def validate_pleasant_habit_fields(
    is_pleasant: bool,
    related_habit: object | None,
    reward: str | None,
) -> None:
    """Проверяет, что у приятной привычки нет related и reward.

    Args:
        is_pleasant: Флаг приятной привычки.
        related_habit: Связанная привычка.
        reward: Текст награды.

    Raises:
        ValidationError: Если у приятной привычки заполнены поля награды.
    """
    if not is_pleasant:
        return
    if related_habit or reward:
        raise ValidationError("У приятной привычки не должно быть награды или связанной привычки.")


def validate_useful_habit_has_reward(
    is_pleasant: bool,
    related_habit: object | None,
    reward: str | None,
) -> None:
    """Проверяет, что полезная привычка имеет награду или связанную приятную.

    Args:
        is_pleasant: Флаг приятной привычки.
        related_habit: Связанная приятная привычка.
        reward: Текст награды.

    Raises:
        ValidationError: Если у полезной привычки нет награды.
    """
    if is_pleasant:
        return
    if not related_habit and not reward:
        raise ValidationError("Полезной привычке нужна награда или связанная приятная привычка.")


def validate_related_habit_owner(
    related_habit: object | None,
    user: object | None,
) -> None:
    """Проверяет, что связанная привычка приятная и принадлежит тому же пользователю.

    Args:
        related_habit: Связанная привычка.
        user: Владелец сохраняемой привычки.

    Raises:
        ValidationError: Если связь некорректна.
    """
    from habits.models import Habit

    if related_habit is None:
        return
    if not isinstance(related_habit, Habit):
        return
    if not related_habit.is_pleasant:
        raise ValidationError("Связанная привычка должна быть приятной.")
    if user is not None and related_habit.user_id != getattr(user, "pk", None):
        raise ValidationError("Связанная привычка должна принадлежать вам.")


def run_habit_validators(
    *,
    user: object | None,
    place: str,
    time: object,
    action: str,
    is_pleasant: bool,
    related_habit: object | None,
    periodicity: int,
    reward: str,
    duration: int,
) -> None:
    """Запускает все правила валидации для набора полей Habit.

    Args:
        user: Владелец привычки.
        place: Место выполнения.
        time: Время напоминания.
        action: Описание действия.
        is_pleasant: Приятная или полезная привычка.
        related_habit: Связанная приятная привычка.
        periodicity: Периодичность в днях.
        reward: Текст награды.
        duration: Длительность в секундах.

    Raises:
        ValidationError: При нарушении любого правила.
    """
    validate_duration_seconds(duration)
    validate_periodicity_days(periodicity)
    validate_not_both_related_and_reward(related_habit, reward)
    validate_pleasant_habit_fields(is_pleasant, related_habit, reward)
    validate_useful_habit_has_reward(is_pleasant, related_habit, reward)
    validate_related_habit_owner(related_habit, user)
