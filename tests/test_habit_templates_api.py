"""Тесты каталога шаблонов и from-template."""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from habits.models import Habit, HabitTemplate
from users.models import User


class HabitTemplatesAPITestCase(APITestCase):
    """Проверяет GET templates и POST from-template."""

    def setUp(self) -> None:
        """Создаёт пользователя с JWT."""
        self.user = User.objects.create_user(email="tpl@example.com", password="StrongPass123!")
        token_response = self.client.post(
            reverse("token_obtain_pair"),
            {"email": "tpl@example.com", "password": "StrongPass123!"},
            format="json",
        )
        self.auth = {"HTTP_AUTHORIZATION": f"Bearer {token_response.data['access']}"}

    def test_templates_list_after_seed(self) -> None:
        """Каталог содержит 29 шаблонов (13 pleasant + 16 useful)."""
        response = self.client.get(reverse("habits:habit-template-list"), **self.auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(HabitTemplate.objects.count(), 29)
        self.assertEqual(response.data["count"], 29)
        first = response.data["results"][0]
        self.assertIn("slug", first)
        self.assertNotIn("telegram_chat_id", first)

    def test_from_template_pleasant_creates_one(self) -> None:
        """POST from-template для pleasant создаёт одну привычку."""
        template = HabitTemplate.objects.filter(is_pleasant=True).first()
        assert template is not None
        before = Habit.objects.filter(user=self.user).count()
        response = self.client.post(
            reverse("habits:habit-from-template", kwargs={"pk": template.pk}),
            **self.auth,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.filter(user=self.user).count(), before + 1)
        habit = Habit.objects.get(pk=response.data["id"])
        self.assertTrue(habit.is_pleasant)
        self.assertFalse(habit.is_public)

    def test_from_template_useful_with_related_creates_pair(self) -> None:
        """POST useful с suggested_related создаёт пару привычек."""
        template = HabitTemplate.objects.filter(
            is_pleasant=False,
            suggested_related_template__isnull=False,
        ).first()
        assert template is not None
        before = Habit.objects.filter(user=self.user).count()
        response = self.client.post(
            reverse("habits:habit-from-template", kwargs={"pk": template.pk}),
            **self.auth,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.filter(user=self.user).count(), before + 2)

    def test_from_template_unknown_returns_404(self) -> None:
        """POST с несуществующим id шаблона → 404."""
        response = self.client.post(
            reverse("habits:habit-from-template", kwargs={"pk": 999999}),
            **self.auth,
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
