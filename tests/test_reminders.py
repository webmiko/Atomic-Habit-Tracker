"""Тесты Celery-задачи send_habit_reminders и email-напоминаний."""

from datetime import time, timedelta
from unittest.mock import MagicMock, patch

import pytest
from django.core import mail
from django.utils import timezone

from habits.models import Habit
from habits.tasks import send_habit_reminders
from users.models import User


def _create_useful_habit(
    user: User,
    *,
    habit_time: time,
    periodicity: int = 1,
    last_notified_at: object = None,
) -> Habit:
    """Создаёт полезную привычку для тестов напоминаний."""
    return Habit.objects.create(
        user=user,
        place="Дом",
        time=habit_time,
        action="Чтение",
        is_pleasant=False,
        reward="чай",
        duration=60,
        periodicity=periodicity,
        last_notified_at=last_notified_at,
    )


def test_send_reminder_email_in_outbox(db: None) -> None:
    """send_reminder кладёт письмо в mail.outbox."""
    from users.services.email import send_reminder

    user = User.objects.create_user(email="mail@example.com", password="StrongPass123!")
    habit = _create_useful_habit(user, habit_time=time(9, 0))
    send_reminder(user, habit)
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["mail@example.com"]
    assert "Чтение" in mail.outbox[0].body


@pytest.mark.django_db
@patch("habits.tasks.send_message")
@patch("habits.tasks.timezone.localtime")
def test_task_sends_email_when_due(mock_localtime: MagicMock, mock_tg: MagicMock) -> None:
    """Задача отправляет email в текущую минуту и обновляет last_notified_at."""
    fixed_now = timezone.now().replace(hour=8, minute=30, second=0, microsecond=0)
    mock_localtime.return_value = fixed_now

    user = User.objects.create_user(
        email="due@example.com",
        password="StrongPass123!",
        notify_by_email=True,
        notify_by_telegram=False,
    )
    habit = _create_useful_habit(user, habit_time=time(8, 30))

    count = send_habit_reminders()
    habit.refresh_from_db()

    assert count == 1
    assert habit.last_notified_at is not None
    assert len(mail.outbox) == 1
    mock_tg.assert_not_called()


@pytest.mark.django_db
@patch("habits.tasks.send_message")
@patch("habits.tasks.timezone.localtime")
def test_task_skips_pleasant_habit(mock_localtime: MagicMock, mock_tg: MagicMock) -> None:
    """Приятные привычки не получают напоминаний."""
    fixed_now = timezone.now().replace(hour=10, minute=0, second=0, microsecond=0)
    mock_localtime.return_value = fixed_now

    user = User.objects.create_user(email="pleasant@example.com", password="StrongPass123!")
    Habit.objects.create(
        user=user,
        place="Кухня",
        time=time(10, 0),
        action="Вода",
        is_pleasant=True,
        duration=30,
        periodicity=1,
    )

    assert send_habit_reminders() == 0
    assert len(mail.outbox) == 0


@pytest.mark.django_db
@patch("habits.tasks.send_message")
@patch("habits.tasks.timezone.localtime")
def test_task_respects_periodicity(mock_localtime: MagicMock, mock_tg: MagicMock) -> None:
    """Не напоминает раньше интервала periodicity дней."""
    fixed_now = timezone.now().replace(hour=11, minute=15, second=0, microsecond=0)
    mock_localtime.return_value = fixed_now

    user = User.objects.create_user(email="period@example.com", password="StrongPass123!")
    yesterday = timezone.now() - timedelta(days=1)
    habit = _create_useful_habit(
        user,
        habit_time=time(11, 15),
        periodicity=2,
        last_notified_at=yesterday,
    )

    assert send_habit_reminders() == 0
    habit.refresh_from_db()
    assert habit.last_notified_at == yesterday


@pytest.mark.django_db
@patch("habits.tasks.send_message")
@patch("habits.tasks.timezone.localtime")
def test_task_sends_telegram_when_enabled(mock_localtime: MagicMock, mock_tg: MagicMock) -> None:
    """При notify_by_telegram вызывается send_message."""
    fixed_now = timezone.now().replace(hour=12, minute=45, second=0, microsecond=0)
    mock_localtime.return_value = fixed_now

    user = User.objects.create_user(
        email="tgrem@example.com",
        password="StrongPass123!",
        notify_by_email=False,
        notify_by_telegram=True,
        telegram_chat_id="555666777",
    )
    _create_useful_habit(user, habit_time=time(12, 45))

    count = send_habit_reminders()

    assert count == 1
    mock_tg.assert_called_once()
    assert mock_tg.call_args.args[0] == "555666777"
    assert "Чтение" in mock_tg.call_args.args[1]
