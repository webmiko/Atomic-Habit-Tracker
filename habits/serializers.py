"""Сериализаторы привычек."""

from typing import cast

from rest_framework import serializers

from habits.models import Habit, HabitTemplate
from habits.validators import run_habit_validators


class HabitSerializer(serializers.ModelSerializer):
    """Сериализатор создания и изменения личной привычки."""

    related_habit = serializers.PrimaryKeyRelatedField(
        queryset=Habit.objects.none(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Habit
        fields = (
            "id",
            "user",
            "place",
            "time",
            "action",
            "is_pleasant",
            "related_habit",
            "periodicity",
            "reward",
            "duration",
            "is_public",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "user", "created_at", "updated_at")

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Ограничивает выбор related_habit приятными привычками текущего user."""
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated:
            self.fields["related_habit"].queryset = Habit.objects.filter(
                user=user,
                is_pleasant=True,
            )

    def validate(self, attrs: dict[str, object]) -> dict[str, object]:
        """Применяет те же правила, что и ``Habit.clean()``.

        Args:
            attrs: Поля из запроса, объединённые с существующим объектом при PATCH.

        Returns:
            Проверенные атрибуты.

        Raises:
            serializers.ValidationError: При нарушении бизнес-правил.
        """
        instance = getattr(self, "instance", None)
        user = attrs.get("user") or (instance.user if instance else None)
        if user is None and self.context.get("request"):
            user = self.context["request"].user

        merged = {
            "place": attrs.get("place", getattr(instance, "place", "")),
            "time": attrs.get("time", getattr(instance, "time", None)),
            "action": attrs.get("action", getattr(instance, "action", "")),
            "is_pleasant": attrs.get("is_pleasant", getattr(instance, "is_pleasant", False)),
            "related_habit": attrs.get("related_habit", getattr(instance, "related_habit", None)),
            "periodicity": attrs.get("periodicity", getattr(instance, "periodicity", 1)),
            "reward": attrs.get("reward", getattr(instance, "reward", "")),
            "duration": attrs.get("duration", getattr(instance, "duration", None)),
        }

        try:
            run_habit_validators(
                user=user,
                place=str(merged["place"]),
                time=merged["time"],
                action=str(merged["action"]),
                is_pleasant=bool(merged["is_pleasant"]),
                related_habit=merged["related_habit"],
                periodicity=cast(int, merged["periodicity"]),
                reward=str(merged["reward"] or ""),
                duration=cast(int, merged["duration"]),
            )
        except Exception as exc:
            from django.core.exceptions import ValidationError as DjangoValidationError

            if isinstance(exc, DjangoValidationError):
                raise serializers.ValidationError(exc.messages) from exc
            raise

        return attrs


class HabitPublicSerializer(serializers.ModelSerializer):
    """Публичная карточка привычки без PII владельца."""

    author_name = serializers.SerializerMethodField()
    formula = serializers.SerializerMethodField()
    related_action = serializers.SerializerMethodField()

    class Meta:
        model = Habit
        fields = (
            "id",
            "action",
            "place",
            "time",
            "duration",
            "periodicity",
            "is_pleasant",
            "reward",
            "related_action",
            "author_name",
            "formula",
        )
        read_only_fields = fields

    def get_author_name(self, obj: Habit) -> str:
        """Возвращает отображаемое имя автора без email."""
        name = (obj.user.public_display_name or "").strip()
        return name if name else "Участник"

    def get_formula(self, obj: Habit) -> str:
        """Формулировка привычки в духе «место — время — действие»."""
        time_str = obj.time.strftime("%H:%M")
        return f"В {obj.place} в {time_str} я буду {obj.action}"

    def get_related_action(self, obj: Habit) -> str | None:
        """Текст связанной приятной привычки без id чужой записи."""
        if obj.related_habit_id:
            return str(obj.related_habit.action)
        return None


class HabitTemplateSerializer(serializers.ModelSerializer):
    """Карточка шаблона в каталоге (read-only)."""

    suggested_related_slug = serializers.SlugRelatedField(
        source="suggested_related_template",
        slug_field="slug",
        read_only=True,
    )

    class Meta:
        model = HabitTemplate
        fields = (
            "id",
            "slug",
            "action",
            "place",
            "time",
            "duration",
            "periodicity",
            "is_pleasant",
            "reward",
            "suggested_related_slug",
            "category",
            "tagline",
            "pair_group",
            "sort_order",
            "is_featured",
        )
        read_only_fields = fields
