"""Тесты точки входа."""

from atomic_habit_tracker import __version__


def test_version_is_semver_like() -> None:
    """Версия задана и не пустая."""
    parts = __version__.split(".")
    assert len(parts) >= 2
    assert all(part.isdigit() for part in parts)
