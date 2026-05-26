"""Маршруты API привычек."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from habits.views import (
    HabitFromTemplateView,
    HabitPublicViewSet,
    HabitTemplateViewSet,
    HabitViewSet,
)

app_name = "habits"

router = DefaultRouter()
router.register(r"habits/public", HabitPublicViewSet, basename="habit-public")
router.register(r"habits/templates", HabitTemplateViewSet, basename="habit-template")
router.register(r"habits", HabitViewSet, basename="habit")

urlpatterns = [
    path(
        "habits/from-template/<int:pk>/",
        HabitFromTemplateView.as_view(),
        name="habit-from-template",
    ),
    path("", include(router.urls)),
]
