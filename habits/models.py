"""Модели привычек пользователя."""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from habits.validators import run_habit_validators, run_template_validators


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


class HabitTemplate(models.Model):
    """Шаблон привычки из каталога (без владельца и флага публичности).

    Attributes:
        slug: Уникальный идентификатор для API.
        action: Краткое описание действия.
        place: Место выполнения.
        time: Рекомендуемое время напоминания.
        duration: Длительность в секундах (не более 120).
        periodicity: Интервал между напоминаниями в днях (1–7).
        is_pleasant: Приятный шаблон без награды.
        suggested_related_template: Приятный шаблон для полезного.
        reward: Текстовая награда вместо связи.
        category: Рубрика витрины каталога.
        tagline: Однострочное описание на карточке.
        pair_group: Slug пары «полезная + награда».
        sort_order: Порядок в списке каталога.
        is_featured: Показывать в блоке «рекомендуем».
    """

    CATEGORY_CHOICES = [
        ("health", "здоровье"),
        ("focus", "фокус"),
        ("calm", "спокойствие"),
        ("home", "дом"),
        ("social", "общение"),
        ("learning", "обучение"),
    ]

    place = models.CharField("место", max_length=200)
    time = models.TimeField("время")
    action = models.CharField("действие", max_length=255)
    is_pleasant = models.BooleanField("приятная", default=False)
    suggested_related_template = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="linked_useful_templates",
        verbose_name="рекомендуемая приятная",
    )
    periodicity = models.PositiveSmallIntegerField(
        "периодичность (дней)",
        default=1,
    )
    reward = models.CharField("награда", max_length=255, blank=True, default="")
    duration = models.PositiveSmallIntegerField("длительность (сек)")
    category = models.CharField(
        "категория",
        max_length=32,
        choices=CATEGORY_CHOICES,
        default="health",
    )
    slug = models.SlugField("slug", max_length=64, unique=True)
    tagline = models.CharField("подпись", max_length=119, blank=True, default="")
    pair_group = models.SlugField("группа пары", max_length=64, blank=True, default="")
    sort_order = models.PositiveIntegerField("порядок", default=0)
    is_featured = models.BooleanField("рекомендуем", default=False)

    class Meta:
        verbose_name = "шаблон привычки"
        verbose_name_plural = "шаблоны привычек"
        ordering = ("sort_order", "slug")

    def __str__(self) -> str:
        return str(self.action)

    def clean(self) -> None:
        """Проверяет бизнес-правила шаблона перед сохранением."""
        super().clean()
        try:
            run_template_validators(
                is_pleasant=self.is_pleasant,
                suggested_related_template=self.suggested_related_template,
                periodicity=self.periodicity,
                reward=self.reward,
                duration=self.duration,
            )
        except ValidationError as exc:
            if hasattr(exc, "error_dict"):
                raise
            raise ValidationError(exc.messages) from exc
