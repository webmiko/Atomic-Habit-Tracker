"""Тесты регистрации, JWT и профиля /api/users/me/."""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User


class RegisterAPITestCase(APITestCase):
    """Проверяет POST /api/users/register/."""

    def test_register_creates_user(self) -> None:
        """Успешная регистрация возвращает 201 и сохраняет email."""
        response = self.client.post(
            reverse("users:register"),
            {"email": "new@example.com", "password": "StrongPass123!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="new@example.com").exists())
        self.assertNotIn("password", response.data)

    def test_register_duplicate_email_returns_400(self) -> None:
        """Повторный email возвращает ошибку валидации."""
        User.objects.create_user(email="dup@example.com", password="StrongPass123!")
        response = self.client.post(
            reverse("users:register"),
            {"email": "dup@example.com", "password": "StrongPass123!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TokenAPITestCase(APITestCase):
    """Проверяет выдачу и обновление JWT."""

    def setUp(self) -> None:
        """Создаёт пользователя для получения токена."""
        self.user = User.objects.create_user(email="token@example.com", password="StrongPass123!")

    def test_obtain_token_with_email(self) -> None:
        """POST /api/token/ принимает email и пароль."""
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"email": "token@example.com", "password": "StrongPass123!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_obtain_token_wrong_password_returns_401(self) -> None:
        """Неверный пароль не выдаёт токен."""
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"email": "token@example.com", "password": "wrong"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserMeAPITestCase(APITestCase):
    """Проверяет GET/PATCH /api/users/me/."""

    def setUp(self) -> None:
        """Создаёт пользователя и JWT."""
        self.user = User.objects.create_user(
            email="me@example.com",
            password="StrongPass123!",
            public_display_name="Ник",
        )
        token_response = self.client.post(
            reverse("token_obtain_pair"),
            {"email": "me@example.com", "password": "StrongPass123!"},
            format="json",
        )
        self.access = token_response.data["access"]

    def test_me_without_token_returns_401(self) -> None:
        """Запрос без Authorization возвращает 401."""
        response = self.client.get(reverse("users:me"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_get_returns_profile(self) -> None:
        """GET возвращает профиль без telegram_chat_id."""
        response = self.client.get(
            reverse("users:me"),
            HTTP_AUTHORIZATION=f"Bearer {self.access}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "me@example.com")
        self.assertEqual(response.data["public_display_name"], "Ник")
        self.assertNotIn("telegram_chat_id", response.data)
        self.assertIn("telegram_linked", response.data)

    def test_me_patch_updates_display_name(self) -> None:
        """PATCH обновляет public_display_name."""
        response = self.client.patch(
            reverse("users:me"),
            {"public_display_name": "Новое имя"},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.access}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.public_display_name, "Новое имя")
