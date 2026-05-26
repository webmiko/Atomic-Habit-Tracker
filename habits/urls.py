"""Маршруты API привычек."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from habits.views import HabitPublicViewSet, HabitViewSet

app_name = "habits"

router = DefaultRouter()
router.register(r"habits/public", HabitPublicViewSet, basename="habit-public")
router.register(r"habits", HabitViewSet, basename="habit")

urlpatterns = [
    path("", include(router.urls)),
]
