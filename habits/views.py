"""HTTP-представления API привычек."""

from django.db.models import QuerySet
from rest_framework import viewsets
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.serializers import BaseSerializer

from habits.models import Habit
from habits.paginators import HabitPageNumberPagination
from habits.permissions import IsOwner
from habits.serializers import HabitSerializer


class HabitViewSet(viewsets.ModelViewSet):
    """CRUD личных привычек текущего пользователя."""

    serializer_class = HabitSerializer
    pagination_class = HabitPageNumberPagination

    def get_queryset(self) -> QuerySet[Habit]:
        """Возвращает только привычки авторизованного пользователя."""
        return Habit.objects.filter(user=self.request.user)

    def get_permissions(self) -> list[BasePermission]:
        """Требует JWT; для detail-действий — дополнительно IsOwner."""
        if self.action in ("retrieve", "update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsOwner()]
        return [IsAuthenticated()]

    def perform_create(self, serializer: BaseSerializer) -> None:
        """Привязывает новую привычку к текущему пользователю.

        Args:
            serializer: Провалидированный сериализатор.
        """
        serializer.save(user=self.request.user)
