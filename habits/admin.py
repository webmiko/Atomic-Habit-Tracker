"""Регистрация модели Habit в админ-панели."""

from django.contrib import admin

from habits.models import Habit


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    """Просмотр и правка привычек в Django Admin."""

    list_display = (
        "action",
        "user",
        "time",
        "is_pleasant",
        "is_public",
        "periodicity",
        "duration",
    )
    list_filter = ("is_pleasant", "is_public", "user")
    search_fields = ("action", "place", "user__email")
    raw_id_fields = ("user", "related_habit")
    readonly_fields = ("created_at", "updated_at", "last_notified_at")
