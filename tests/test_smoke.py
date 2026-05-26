"""Smoke-тесты: основные URL отвечают ожидаемым кодом."""

import pytest
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
def test_smoke_public_and_auth_routes() -> None:
    """Проверяет доступность ключевых маршрутов без 500."""
    client = Client()
    checks: list[tuple[str, int]] = [
        ("/admin/login/", 200),
        (reverse("users:register"), 405),
        (reverse("token_obtain_pair"), 405),
        ("/swagger/", 200),
        ("/redoc/", 200),
        ("/swagger.json", 200),
        (reverse("habits:habit-list"), 401),
        (reverse("habits:habit-public-list"), 401),
        (reverse("habits:habit-template-list"), 401),
        (reverse("users:me"), 401),
        (reverse("users:telegram-link"), 401),
    ]
    for path, expected_status in checks:
        if path.endswith("swagger.json"):
            response = client.get(path, HTTP_ACCEPT="application/json")
        else:
            response = client.get(path)
        assert response.status_code == expected_status, (
            f"{path}: expected {expected_status}, got {response.status_code}"
        )
