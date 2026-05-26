"""Маршруты API привычек."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from habits.views import HabitViewSet

app_name = "habits"

router = DefaultRouter()
router.register("habits", HabitViewSet, basename="habit")

urlpatterns = [
    path("", include(router.urls)),
]
