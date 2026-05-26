"""Celery-задачи напоминаний о привычках."""

from __future__ import annotations

import logging
from datetime import datetime, time

from django.utils import timezone

from celery import shared_task
from habits.models import Habit
from users.models import User
from users.services.email import send_reminder
from users.services.telegram import TelegramServiceError, send_message

logger = logging.getLogger(__name__)


def _time_matches_current_minute(habit_time: time, now: datetime) -> bool:
    """Проверяет, что время привычки совпадает с текущей минутой (локально)."""
    return habit_time.hour == now.hour and habit_time.minute == now.minute


def _periodicity_allows_notify(habit: Habit, now: datetime) -> bool:
    """Проверяет, прошёл ли интервал periodicity с последнего напоминания."""
    if habit.last_notified_at is None:
        return True
    last_local = timezone.localtime(habit.last_notified_at)
    days_since = (now.date() - last_local.date()).days
    return bool(days_since >= habit.periodicity)


def _should_notify(habit: Habit, now: datetime) -> bool:
    """Возвращает True, если полезной привычке пора отправить напоминание."""
    if habit.is_pleasant:
        return False
    if not _time_matches_current_minute(habit.time, now):
        return False
    return _periodicity_allows_notify(habit, now)


def _notify_user(habit: Habit, user: User) -> bool:
    """Отправляет напоминание по включённым каналам.

    Args:
        habit: Привычка для текста сообщения.
        user: Владелец с флагами notify_*.

    Returns:
        True, если хотя бы один канал отработал успешно.
    """
    from users.services.email import build_reminder_message

    message = build_reminder_message(habit)
    success = False

    if user.notify_by_email and user.email:
        try:
            send_reminder(user, habit)
            success = True
        except Exception:
            logger.exception("Email reminder failed habit_id=%s user_id=%s", habit.pk, user.pk)

    if user.notify_by_telegram and user.telegram_chat_id:
        try:
            send_message(str(user.telegram_chat_id), message)
            success = True
        except TelegramServiceError:
            logger.exception("Telegram reminder failed habit_id=%s user_id=%s", habit.pk, user.pk)

    return success


@shared_task(name="habits.tasks.send_habit_reminders")
def send_habit_reminders() -> int:
    """Рассылает напоминания по полезным привычкам в текущую минуту.

    Returns:
        Число привычек, для которых обновлён ``last_notified_at``.
    """
    now = timezone.localtime()
    habits = Habit.objects.filter(is_pleasant=False).select_related("user")
    sent_count = 0

    for habit in habits:
        if not _should_notify(habit, now):
            continue
        if _notify_user(habit, habit.user):
            habit.last_notified_at = timezone.now()
            habit.save(update_fields=["last_notified_at"])
            sent_count += 1

    return sent_count
