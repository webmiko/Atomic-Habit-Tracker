"""HTTP-представления API привычек."""

from django.db.models import QuerySet
from django.http import Http404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.views import APIView

from habits.models import Habit, HabitTemplate
from habits.paginators import HabitPageNumberPagination
from habits.permissions import IsOwner
from habits.serializers import (
    HabitPublicSerializer,
    HabitSerializer,
    HabitTemplateSerializer,
)
from habits.services import copy_habit_to_user, create_habit_from_template


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


class HabitPublicViewSet(viewsets.ReadOnlyModelViewSet):
    """Лента публичных привычек: просмотр и копирование к себе."""

    serializer_class = HabitPublicSerializer
    pagination_class = HabitPageNumberPagination
    http_method_names = ("get", "head", "options", "post", "put", "patch", "delete")

    def get_queryset(self) -> QuerySet[Habit]:
        """Публичные привычки других пользователей."""
        return (
            Habit.objects.filter(is_public=True)
            .exclude(user=self.request.user)
            .select_related("user", "related_habit")
        )

    def update(self, request: Request, *args: object, **kwargs: object) -> Response:
        """Запрещает изменение чужих публичных привычек."""
        raise Http404

    def partial_update(self, request: Request, *args: object, **kwargs: object) -> Response:
        """Запрещает частичное изменение публичных привычек."""
        raise Http404

    def destroy(self, request: Request, *args: object, **kwargs: object) -> Response:
        """Запрещает удаление через public-маршрут."""
        raise Http404

    @action(detail=True, methods=["post"])
    def copy(self, request: Request, pk: int | None = None) -> Response:
        """Создаёт личную копию публичной привычки.

        Args:
            request: HTTP-запрос с JWT.
            pk: Id публичной привычки.

        Returns:
            JSON созданной привычки (201).
        """
        habit = self.get_object()
        copied = copy_habit_to_user(habit, request.user)
        serializer = HabitSerializer(copied, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class HabitTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """Каталог шаблонов привычек (только чтение)."""

    serializer_class = HabitTemplateSerializer
    pagination_class = HabitPageNumberPagination
    queryset = HabitTemplate.objects.all()


class HabitFromTemplateView(APIView):
    """Создание привычки из шаблона каталога."""

    permission_classes = (IsAuthenticated,)

    def post(self, request: Request, pk: int) -> Response:
        """Создаёт привычку(и) по шаблону.

        Args:
            request: HTTP-запрос с JWT.
            pk: Id шаблона.

        Returns:
            JSON созданной привычки (201) или 404.
        """
        try:
            template = HabitTemplate.objects.get(pk=pk)
        except HabitTemplate.DoesNotExist as exc:
            raise Http404 from exc

        habit = create_habit_from_template(template, request.user)
        serializer = HabitSerializer(habit, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
