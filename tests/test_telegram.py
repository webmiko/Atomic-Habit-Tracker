"""Тесты Telegram-сервиса, кодов привязки и API."""

from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import TelegramLinkCode, User
from users.services.link_codes import CODE_TTL_MINUTES, create_link_code, redeem_link_code
from users.services.telegram import TelegramServiceError, send_message


class TelegramLinkAPITestCase(APITestCase):
    """Проверяет POST /api/users/telegram/link/."""

    def setUp(self) -> None:
        """Создаёт пользователя и JWT."""
        self.user = User.objects.create_user(email="tg@example.com", password="StrongPass123!")
        token_response = self.client.post(
            reverse("token_obtain_pair"),
            {"email": "tg@example.com", "password": "StrongPass123!"},
            format="json",
        )
        self.auth = {"HTTP_AUTHORIZATION": f"Bearer {token_response.data['access']}"}

    def test_link_returns_code_without_bot_token(self) -> None:
        """POST возвращает код и TTL, без TELEGRAM_BOT_TOKEN."""
        with patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "secret-token-123"}):
            response = self.client.post(reverse("users:telegram-link"), **self.auth)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("code", response.data)
        self.assertEqual(response.data["expires_in_minutes"], CODE_TTL_MINUTES)
        self.assertNotIn("TELEGRAM_BOT_TOKEN", str(response.data))
        self.assertNotIn("secret-token", str(response.data))
        self.assertTrue(
            TelegramLinkCode.objects.filter(user=self.user, code=response.data["code"]).exists(),
        )

    def test_link_without_auth_returns_401(self) -> None:
        """POST без JWT возвращает 401."""
        response = self.client.post(reverse("users:telegram-link"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_still_hides_chat_id_after_link(self) -> None:
        """GET /me/ не раскрывает telegram_chat_id после привязки."""
        link = create_link_code(self.user)
        redeem_link_code(link.code, "123456789")
        response = self.client.get(reverse("users:me"), **self.auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["telegram_linked"])
        self.assertNotIn("telegram_chat_id", response.data)


class TelegramServiceTestCase(APITestCase):
    """Проверяет send_message и redeem_link_code."""

    def setUp(self) -> None:
        """Создаёт пользователя для привязки."""
        self.user = User.objects.create_user(email="svc@example.com", password="StrongPass123!")

    @patch("users.services.telegram.requests.post")
    def test_send_message_calls_api(self, mock_post: MagicMock) -> None:
        """send_message вызывает sendMessage с chat_id и текстом."""
        mock_post.return_value = MagicMock(ok=True, status_code=200)
        with patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "123:ABC"}):
            send_message("42", "Привет")
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args.kwargs
        self.assertEqual(call_kwargs["json"]["chat_id"], "42")
        self.assertEqual(call_kwargs["json"]["text"], "Привет")

    def test_send_message_without_token_raises(self) -> None:
        """Без TELEGRAM_BOT_TOKEN поднимается TelegramServiceError."""
        with (
            patch.dict("os.environ", {}, clear=True),
            pytest.raises(TelegramServiceError),
        ):
            send_message("1", "test")

    @patch("users.services.telegram.requests.post")
    def test_send_message_api_error_raises(self, mock_post: MagicMock) -> None:
        """Ошибка Bot API поднимает TelegramServiceError без текста TG в исключении."""
        mock_post.return_value = MagicMock(ok=False, status_code=400, text="Bad Request: forbidden")
        with (
            patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "tok"}),
            pytest.raises(TelegramServiceError) as exc_info,
        ):
            send_message("1", "test")
        self.assertNotIn("forbidden", str(exc_info.value).lower())

    def test_redeem_link_code_sets_chat_id(self) -> None:
        """Валидный код сохраняет telegram_chat_id и удаляет код."""
        link = create_link_code(self.user)
        message = redeem_link_code(link.code, "999888777")
        self.user.refresh_from_db()
        self.assertEqual(self.user.telegram_chat_id, "999888777")
        self.assertFalse(TelegramLinkCode.objects.filter(pk=link.pk).exists())
        self.assertIn("привязан", message.lower())

    def test_redeem_expired_code_fails(self) -> None:
        """Истёкший код не привязывает chat_id."""
        link = create_link_code(self.user)
        link.expires_at = timezone.now() - timedelta(minutes=1)
        link.save(update_fields=["expires_at"])
        message = redeem_link_code(link.code, "111")
        self.user.refresh_from_db()
        self.assertIsNone(self.user.telegram_chat_id)
        self.assertIn("истёк", message.lower())

    def test_redeem_unknown_code(self) -> None:
        """Несуществующий код возвращает понятное сообщение."""
        message = redeem_link_code("ZZZZZZZZ", "111")
        self.assertIn("не найден", message.lower())
