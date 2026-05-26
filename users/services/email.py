"""Отправка email-напоминаний о привычках."""

from django.conf import settings
from django.core.mail import send_mail

from habits.models import Habit
from users.models import User

REMINDER_SUBJECT = "Напоминание о привычке"


def build_reminder_message(habit: Habit) -> str:
    """Формирует текст напоминания по полям привычки.

    Args:
        habit: Полезная привычка с заполненными place, time, action.

    Returns:
        Строка для email и Telegram.
    """
    time_str = habit.time.strftime("%H:%M")
    return f"Напоминание: {habit.action} в {time_str} в {habit.place}"


def send_reminder(user: User, habit: Habit) -> None:
    """Отправляет email-напоминание владельцу привычки.

    Args:
        user: Получатель с адресом email.
        habit: Привычка, о которой напоминаем.

    Raises:
        Exception: Пробрасывает ошибки ``send_mail`` вызывающему коду.
    """
    message = build_reminder_message(habit)
    send_mail(
        REMINDER_SUBJECT,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
