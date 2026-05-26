"""Права доступа к привычкам."""

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from habits.models import Habit


class IsOwner(BasePermission):
    """Разрешает доступ только владельцу привычки."""

    def has_object_permission(self, request: Request, view: APIView, obj: Habit) -> bool:
        """Проверяет, что объект принадлежит текущему пользователю.

        Args:
            request: HTTP-запрос с JWT.
            view: ViewSet, обрабатывающий запрос.
            obj: Экземпляр Habit.

        Returns:
            True, если user совпадает с владельцем привычки.
        """
        return bool(obj.user_id == request.user.pk)
