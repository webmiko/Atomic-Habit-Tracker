"""Регистрация модели User в админ-панели Django."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from users.models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Админка пользователей: email, профиль и флаги оповещений."""

    ordering = ("email",)
    list_display = (
        "email",
        "public_display_name",
        "notify_by_email",
        "notify_by_telegram",
        "is_staff",
        "is_active",
    )
    search_fields = ("email", "public_display_name")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Профиль",
            {"fields": ("public_display_name", "notify_by_email", "notify_by_telegram")},
        ),
        (
            "Telegram",
            {"fields": ("telegram_chat_id",)},
        ),
        (
            "Права",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        ("Даты", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),)
