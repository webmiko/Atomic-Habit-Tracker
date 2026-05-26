"""Тесты CRUD /api/habits/ и пагинации."""

from datetime import time

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from habits.models import Habit
from users.models import User


class HabitsAPITestCase(APITestCase):
    """Базовый набор для JWT и создания привычек."""

    def setUp(self) -> None:
        """Создаёт пользователя и заголовок Authorization."""
        self.user = User.objects.create_user(email="owner@example.com", password="StrongPass123!")
        self.other = User.objects.create_user(email="other@example.com", password="StrongPass123!")
        token_response = self.client.post(
            reverse("token_obtain_pair"),
            {"email": "owner@example.com", "password": "StrongPass123!"},
            format="json",
        )
        self.auth = {"HTTP_AUTHORIZATION": f"Bearer {token_response.data['access']}"}

    def _useful_payload(self, **overrides: object) -> dict[str, object]:
        """Возвращает валидное тело полезной привычки."""
        payload: dict[str, object] = {
            "place": "Парк",
            "time": "07:30:00",
            "action": "Пробежка",
            "is_pleasant": False,
            "reward": "чай",
            "duration": 60,
            "periodicity": 1,
            "is_public": False,
        }
        payload.update(overrides)
        return payload

    def test_create_useful_habit_returns_201(self) -> None:
        """POST создаёт привычку и привязывает её к текущему user."""
        response = self.client.post(
            reverse("habits:habit-list"),
            self._useful_payload(),
            format="json",
            **self.auth,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        habit = Habit.objects.get(pk=response.data["id"])
        self.assertEqual(habit.user_id, self.user.pk)
        self.assertEqual(response.data["user"], self.user.pk)

    def test_create_without_reward_returns_400(self) -> None:
        """POST полезной без награды и related возвращает 400."""
        response = self.client.post(
            reverse("habits:habit-list"),
            self._useful_payload(reward="", related_habit=None),
            format="json",
            **self.auth,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_only_own_habits(self) -> None:
        """GET возвращает только привычки текущего пользователя."""
        Habit.objects.create(
            user=self.user,
            place="Дом",
            time=time(8, 0),
            action="Своя",
            is_pleasant=False,
            reward="чай",
            duration=30,
            periodicity=1,
        )
        Habit.objects.create(
            user=self.other,
            place="Офис",
            time=time(9, 0),
            action="Чужая",
            is_pleasant=False,
            reward="кофе",
            duration=30,
            periodicity=1,
        )
        response = self.client.get(reverse("habits:habit-list"), **self.auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["action"], "Своя")

    def test_pagination_five_per_page(self) -> None:
        """Шесть записей дают две страницы по пять и одну."""
        for index in range(6):
            Habit.objects.create(
                user=self.user,
                place="Дом",
                time=time(8, index % 60),
                action=f"Привычка {index}",
                is_pleasant=False,
                reward="чай",
                duration=30,
                periodicity=1,
            )
        page1 = self.client.get(reverse("habits:habit-list"), **self.auth)
        self.assertEqual(page1.status_code, status.HTTP_200_OK)
        self.assertEqual(page1.data["count"], 6)
        self.assertEqual(len(page1.data["results"]), 5)
        self.assertIsNotNone(page1.data["next"])
        self.assertIsNone(page1.data["previous"])

        page2 = self.client.get(page1.data["next"], **self.auth)
        self.assertEqual(page2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(page2.data["results"]), 1)
        self.assertIsNotNone(page2.data["previous"])
        self.assertIsNone(page2.data["next"])

    def test_retrieve_foreign_habit_returns_404(self) -> None:
        """GET чужой привычки возвращает 404."""
        foreign = Habit.objects.create(
            user=self.other,
            place="Офис",
            time=time(10, 0),
            action="Чужая",
            is_pleasant=False,
            reward="чай",
            duration=30,
            periodicity=1,
        )
        response = self.client.get(
            reverse("habits:habit-detail", kwargs={"pk": foreign.pk}),
            **self.auth,
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_updates_is_public(self) -> None:
        """PATCH меняет is_public у своей привычки."""
        habit = Habit.objects.create(
            user=self.user,
            place="Дом",
            time=time(8, 0),
            action="Чтение",
            is_pleasant=False,
            reward="чай",
            duration=30,
            periodicity=1,
            is_public=False,
        )
        response = self.client.patch(
            reverse("habits:habit-detail", kwargs={"pk": habit.pk}),
            {"is_public": True},
            format="json",
            **self.auth,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        habit.refresh_from_db()
        self.assertTrue(habit.is_public)

    def test_delete_own_habit_returns_204(self) -> None:
        """DELETE удаляет свою привычку."""
        habit = Habit.objects.create(
            user=self.user,
            place="Дом",
            time=time(8, 0),
            action="Удаляемая",
            is_pleasant=False,
            reward="чай",
            duration=30,
            periodicity=1,
        )
        response = self.client.delete(
            reverse("habits:habit-detail", kwargs={"pk": habit.pk}),
            **self.auth,
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Habit.objects.filter(pk=habit.pk).exists())

    def test_cannot_link_foreign_pleasant_habit(self) -> None:
        """POST с related_habit другого пользователя возвращает 400."""
        foreign_pleasant = Habit.objects.create(
            user=self.other,
            place="Офис",
            time=time(9, 0),
            action="Чужая приятная",
            is_pleasant=True,
            duration=20,
            periodicity=1,
        )
        response = self.client.post(
            reverse("habits:habit-list"),
            self._useful_payload(reward="", related_habit=foreign_pleasant.pk),
            format="json",
            **self.auth,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_list_returns_401(self) -> None:
        """GET без JWT возвращает 401."""
        response = self.client.get(reverse("habits:habit-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
