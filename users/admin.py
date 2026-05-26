"""Регистрация модели User в админ-панели Django."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from users.models import TelegramLinkCode, User


@admin.register(TelegramLinkCode)
class TelegramLinkCodeAdmin(admin.ModelAdmin):
    """Просмотр активных кодов привязки."""

    list_display = ("code", "user", "expires_at", "created_at")
    list_filter = ("expires_at",)
    search_fields = ("code", "user__email")
    raw_id_fields = ("user",)
    readonly_fields = ("created_at",)


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
