"""Тесты OpenAPI-схемы и CORS."""

import pytest
from django.conf import settings
from django.test import Client


@pytest.mark.django_db
def test_swagger_json_lists_tz_endpoints() -> None:
    """Схема содержит основные URL из ТЗ."""
    response = Client().get("/swagger.json", HTTP_ACCEPT="application/json")
    assert response.status_code == 200
    paths = response.json()["paths"]
    path_keys = list(paths.keys())
    required = [
        "/users/register/",
        "/users/me/",
        "/users/telegram/link/",
        "/token/",
        "/habits/",
        "/habits/public/",
        "/habits/templates/",
    ]
    for required_path in required:
        assert required_path in path_keys, f"Missing {required_path}, got {path_keys}"
    assert any("from-template" in key for key in path_keys)


def test_swagger_ui_returns_200() -> None:
    """Страница Swagger UI открывается."""
    response = Client().get("/swagger/")
    assert response.status_code == 200


def test_redoc_returns_200() -> None:
    """Страница ReDoc открывается."""
    response = Client().get("/redoc/")
    assert response.status_code == 200


def test_swagger_schema_has_no_secret_key() -> None:
    """OpenAPI не содержит SECRET_KEY."""
    response = Client().get("/swagger.json", HTTP_ACCEPT="application/json")
    body = response.content.decode()
    assert "SECRET_KEY" not in body


def test_allowed_hosts_includes_testserver() -> None:
    """ALLOWED_HOSTS содержит testserver для APITestCase."""

    assert "testserver" in settings.ALLOWED_HOSTS


def test_cors_allows_configured_origin_on_preflight() -> None:
    """CORS отвечает на preflight с разрешённого origin."""
    response = Client().options(
        "/api/token/",
        HTTP_ORIGIN="http://localhost:5500",
        HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
    )
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5500"
