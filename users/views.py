"""HTTP-представления регистрации, JWT и профиля."""

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from users.serializers import (
    RegisterSerializer,
    TelegramLinkResponseSerializer,
    UserMeSerializer,
)


class RegisterView(generics.CreateAPIView):
    """Регистрация нового пользователя по email и паролю."""

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)


class UserMeView(APIView):
    """Профиль и настройки авторизованного пользователя."""

    permission_classes = (IsAuthenticated,)

    def get(self, request: Request) -> Response:
        """Возвращает данные профиля текущего пользователя.

        Args:
            request: HTTP-запрос с JWT.

        Returns:
            JSON профиля без telegram_chat_id.
        """
        serializer = UserMeSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request: Request) -> Response:
        """Частично обновляет настройки профиля.

        Args:
            request: HTTP-запрос с полями public_display_name, notify_*.

        Returns:
            Обновлённый JSON профиля.
        """
        serializer = UserMeSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class TelegramLinkView(APIView):
    """Выдача одноразового кода привязки Telegram."""

    permission_classes = (IsAuthenticated,)

    def post(self, request: Request) -> Response:
        """Создаёт код привязки для текущего пользователя.

        Args:
            request: HTTP-запрос с JWT.

        Returns:
            JSON с кодом и временем жизни (без токена бота).
        """
        from users.services.link_codes import CODE_TTL_MINUTES, create_link_code

        link = create_link_code(request.user)
        serializer = TelegramLinkResponseSerializer(
            {"code": link.code, "expires_in_minutes": CODE_TTL_MINUTES},
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
