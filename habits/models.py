"""Модели привычек пользователя."""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from habits.validators import run_habit_validators


class Habit(models.Model):
    """Привычка пользователя с напоминанием и опциональной наградой.

    Attributes:
        user: Владелец записи.
        action: Краткое описание действия.
        place: Место выполнения.
        time: Время ежедневного напоминания.
        duration: Длительность в секундах (не более 120).
        periodicity: Интервал между напоминаниями в днях (1–7).
        is_pleasant: Приятная привычка без собственной награды.
        related_habit: Связанная приятная привычка для полезной.
        reward: Текстовая награда вместо связи.
        is_public: Видимость в ленте сообщества.
        last_notified_at: Время последнего успешного напоминания.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="habits",
        verbose_name="пользователь",
    )
    place = models.CharField("место", max_length=200)
    time = models.TimeField("время")
    action = models.CharField("действие", max_length=255)
    is_pleasant = models.BooleanField("приятная", default=False)
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="linked_useful_habits",
        verbose_name="связанная приятная привычка",
    )
    periodicity = models.PositiveSmallIntegerField(
        "периодичность (дней)",
        default=1,
    )
    reward = models.CharField("награда", max_length=255, blank=True, default="")
    duration = models.PositiveSmallIntegerField("длительность (сек)")
    is_public = models.BooleanField("публичная", default=False)
    last_notified_at = models.DateTimeField(
        "последнее напоминание",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField("создана", auto_now_add=True)
    updated_at = models.DateTimeField("обновлена", auto_now=True)

    class Meta:
        verbose_name = "привычка"
        verbose_name_plural = "привычки"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.action} ({self.user_id})"

    def clean(self) -> None:
        """Проверяет бизнес-правила перед сохранением в БД."""
        super().clean()
        try:
            run_habit_validators(
                user=self.user,
                place=self.place,
                time=self.time,
                action=self.action,
                is_pleasant=self.is_pleasant,
                related_habit=self.related_habit,
                periodicity=self.periodicity,
                reward=self.reward,
                duration=self.duration,
            )
        except ValidationError as exc:
            if hasattr(exc, "error_dict"):
                raise
            raise ValidationError(exc.messages) from exc
