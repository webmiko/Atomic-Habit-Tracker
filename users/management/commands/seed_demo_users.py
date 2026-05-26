"""Демо-пользователи и публичные привычки для проверки фронтенда."""

from datetime import time

from django.core.management.base import BaseCommand

from habits.models import Habit
from users.models import User

DEMO_PASSWORD = "DemoPass123!"


class Command(BaseCommand):
    """Создаёт demo_a (с публичными привычками) и demo_b (зритель)."""

    help = "Создаёт демо-пользователей для проверки ленты сообщества"

    def handle(self, *args: object, **options: object) -> None:
        """Создаёт или обновляет учётные записи и привычки."""
        author, created_a = User.objects.get_or_create(
            email="demo_a@example.com",
            defaults={"public_display_name": "Демо Автор"},
        )
        if created_a or not author.has_usable_password():
            author.set_password(DEMO_PASSWORD)
        author.public_display_name = "Демо Автор"
        author.save()

        viewer, created_b = User.objects.get_or_create(
            email="demo_b@example.com",
            defaults={"public_display_name": "Демо Зритель"},
        )
        if created_b or not viewer.has_usable_password():
            viewer.set_password(DEMO_PASSWORD)
        viewer.public_display_name = "Демо Зритель"
        viewer.save()

        if not Habit.objects.filter(user=author, is_public=True).exists():
            Habit.objects.create(
                user=author,
                place="Парк",
                time=time(7, 0),
                action="Утренняя пробежка 2 мин",
                is_pleasant=False,
                reward="чай с лимоном",
                duration=120,
                periodicity=1,
                is_public=True,
            )
            Habit.objects.create(
                user=author,
                place="Кухня",
                time=time(8, 0),
                action="Выпить стакан воды",
                is_pleasant=False,
                reward="травяной чай",
                duration=30,
                periodicity=1,
                is_public=True,
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Готово: demo_a@example.com / demo_b@example.com, пароль DemoPass123!",
            ),
        )
