"""Тесты безопасности: утечки секретов и CORS."""

import pytest
from django.conf import settings
from django.test import Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from users.models import User


@pytest.mark.django_db
def test_api_responses_do_not_leak_secret_key() -> None:
    """JSON API не содержит SECRET_KEY из настроек."""
    secret = settings.SECRET_KEY or ""
    assert secret

    User.objects.create_user(email="sec@example.com", password="StrongPass123!")
    client = APIClient()
    token = client.post(
        reverse("token_obtain_pair"),
        {"email": "sec@example.com", "password": "StrongPass123!"},
        format="json",
    ).data["access"]

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    endpoints = [
        reverse("users:me"),
        reverse("habits:habit-list"),
        reverse("users:telegram-link"),
    ]
    for url in endpoints:
        response = client.post(url) if "telegram/link" in url else client.get(url)
        body = str(response.data)
        assert secret not in body
        assert "SECRET_KEY" not in body


def test_cors_header_on_api_response() -> None:
    """Ответ API содержит CORS для разрешённого origin."""
    response = Client().get(
        reverse("token_obtain_pair"),
        HTTP_ORIGIN="http://localhost:5500",
    )
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5500"


@pytest.mark.django_db
def test_register_response_has_no_password_field() -> None:
    """Регистрация не возвращает пароль в теле ответа."""
    response = APIClient().post(
        reverse("users:register"),
        {"email": "newsec@example.com", "password": "StrongPass123!"},
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert "password" not in response.data
