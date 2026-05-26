"""Сериализаторы регистрации и профиля пользователя."""

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from users.models import User


class RegisterSerializer(serializers.ModelSerializer):
    """Тело запроса регистрации: email и пароль."""

    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ("email", "password")

    def create(self, validated_data: dict[str, str]) -> User:
        """Создаёт пользователя с хешированным паролем.

        Args:
            validated_data: Поля email и password из запроса.

        Returns:
            Новый экземпляр User.
        """
        password = validated_data.pop("password")
        email = validated_data.pop("email")
        return User.objects.create_user(email=email, password=password)


class UserMeSerializer(serializers.ModelSerializer):
    """Профиль текущего пользователя для личного кабинета."""

    habits_count = serializers.SerializerMethodField()
    public_habits_count = serializers.SerializerMethodField()
    telegram_linked = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "public_display_name",
            "notify_by_email",
            "notify_by_telegram",
            "telegram_linked",
            "habits_count",
            "public_habits_count",
        )
        read_only_fields = (
            "id",
            "email",
            "telegram_linked",
            "habits_count",
            "public_habits_count",
        )

    def get_habits_count(self, obj: User) -> int:
        """Возвращает число личных привычек пользователя."""
        return int(obj.habits.count())

    def get_public_habits_count(self, obj: User) -> int:
        """Возвращает число публичных привычек пользователя."""
        return int(obj.habits.filter(is_public=True).count())

    def get_telegram_linked(self, obj: User) -> bool:
        """Возвращает True, если Telegram привязан (без раскрытия chat_id)."""
        return obj.telegram_linked


class TelegramLinkResponseSerializer(serializers.Serializer):
    """Ответ POST /api/users/telegram/link/ с одноразовым кодом."""

    code = serializers.CharField(read_only=True)
    expires_in_minutes = serializers.IntegerField(read_only=True)
