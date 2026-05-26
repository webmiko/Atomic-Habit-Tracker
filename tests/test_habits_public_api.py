"""Тесты публичной ленты и copy /api/habits/public/."""

from datetime import time

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from habits.models import Habit
from users.models import User


class HabitsPublicAPITestCase(APITestCase):
    """Проверяет ленту, деталь, copy и отсутствие PII."""

    def setUp(self) -> None:
        """Создаёт двух пользователей и JWT для зрителя."""
        self.author = User.objects.create_user(
            email="author@example.com",
            password="StrongPass123!",
            public_display_name="Автор",
        )
        self.viewer = User.objects.create_user(
            email="viewer@example.com",
            password="StrongPass123!",
        )
        token_response = self.client.post(
            reverse("token_obtain_pair"),
            {"email": "viewer@example.com", "password": "StrongPass123!"},
            format="json",
        )
        self.auth = {"HTTP_AUTHORIZATION": f"Bearer {token_response.data['access']}"}

    def _create_public_habit(self, **kwargs: object) -> Habit:
        """Создаёт публичную привычку автора."""
        defaults: dict[str, object] = {
            "user": self.author,
            "place": "Парк",
            "time": time(7, 0),
            "action": "Публичная пробежка",
            "is_pleasant": False,
            "reward": "чай",
            "duration": 60,
            "periodicity": 1,
            "is_public": True,
        }
        defaults.update(kwargs)
        return Habit.objects.create(**defaults)

    def test_list_excludes_own_public_habits(self) -> None:
        """Лента не показывает собственные публичные привычки."""
        self._create_public_habit()
        own_public = Habit.objects.create(
            user=self.viewer,
            place="Дом",
            time=time(8, 0),
            action="Своя публичная",
            is_pleasant=False,
            reward="кофе",
            duration=30,
            periodicity=1,
            is_public=True,
        )
        response = self.client.get(reverse("habits:habit-public-list"), **self.auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertNotEqual(response.data["results"][0]["action"], own_public.action)

    def test_public_json_has_no_pii(self) -> None:
        """Ответ не содержит email, user id и telegram."""
        self._create_public_habit()
        response = self.client.get(reverse("habits:habit-public-list"), **self.auth)
        item = response.data["results"][0]
        self.assertEqual(item["author_name"], "Автор")
        self.assertIn("formula", item)
        self.assertNotIn("user", item)
        self.assertNotIn("email", item)
        self.assertNotIn("telegram_chat_id", item)

    def test_private_habit_detail_returns_404(self) -> None:
        """GET приватной чужой привычки через public → 404."""
        private = Habit.objects.create(
            user=self.author,
            place="Дом",
            time=time(9, 0),
            action="Приватная",
            is_pleasant=False,
            reward="чай",
            duration=30,
            periodicity=1,
            is_public=False,
        )
        response = self.client.get(
            reverse("habits:habit-public-detail", kwargs={"pk": private.pk}),
            **self.auth,
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_public_returns_404(self) -> None:
        """PATCH публичной привычки через public-маршрут → 404."""
        habit = self._create_public_habit()
        response = self.client.patch(
            reverse("habits:habit-public-detail", kwargs={"pk": habit.pk}),
            {"action": "Взлом"},
            format="json",
            **self.auth,
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_copy_creates_private_habit(self) -> None:
        """POST copy создаёт личную копию с is_public=False."""
        habit = self._create_public_habit()
        response = self.client.post(
            reverse("habits:habit-public-copy", kwargs={"pk": habit.pk}),
            **self.auth,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        copied = Habit.objects.get(pk=response.data["id"])
        self.assertEqual(copied.user_id, self.viewer.pk)
        self.assertFalse(copied.is_public)
        self.assertEqual(copied.action, habit.action)

    def test_copy_useful_with_related_creates_pair(self) -> None:
        """Copy полезной с related создаёт приятную и полезную у viewer."""
        pleasant = Habit.objects.create(
            user=self.author,
            place="Кухня",
            time=time(8, 0),
            action="Приятная награда",
            is_pleasant=True,
            duration=20,
            periodicity=1,
            is_public=True,
        )
        useful = Habit.objects.create(
            user=self.author,
            place="Парк",
            time=time(7, 0),
            action="Полезная с связью",
            is_pleasant=False,
            related_habit=pleasant,
            duration=60,
            periodicity=1,
            is_public=True,
        )
        before = Habit.objects.filter(user=self.viewer).count()
        response = self.client.post(
            reverse("habits:habit-public-copy", kwargs={"pk": useful.pk}),
            **self.auth,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.filter(user=self.viewer).count(), before + 2)
        copied = Habit.objects.get(pk=response.data["id"])
        self.assertIsNotNone(copied.related_habit_id)
        self.assertEqual(copied.related_habit.user_id, self.viewer.pk)

    def test_public_list_pagination_five(self) -> None:
        """Шесть чужих публичных → две страницы по 5 и 1."""
        for index in range(6):
            self._create_public_habit(action=f"Публичная {index}")
        page1 = self.client.get(reverse("habits:habit-public-list"), **self.auth)
        self.assertEqual(page1.data["count"], 6)
        self.assertEqual(len(page1.data["results"]), 5)
        page2 = self.client.get(page1.data["next"], **self.auth)
        self.assertEqual(len(page2.data["results"]), 1)
