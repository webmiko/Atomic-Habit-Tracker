"""Management-команда: long polling Telegram-бота для привязки chat_id."""

from __future__ import annotations

import logging
import os
import time
from typing import Any

import requests
from django.core.management.base import BaseCommand

from users.services.link_codes import redeem_link_code
from users.services.telegram import TELEGRAM_API_BASE, TelegramServiceError, send_message

logger = logging.getLogger(__name__)

_START_TEXT = (
    "Привет! Я бот Atomic Habit Tracker.\n\n"
    "1. Войдите в приложение и откройте «Настройки».\n"
    "2. Нажмите «Получить код привязки».\n"
    "3. Отправьте сюда: /link ВАШ_КОД\n\n"
    "После привязки включите notify_by_telegram в профиле."
)


class Command(BaseCommand):
    """Запускает long polling getUpdates и обрабатывает /start и /link."""

    help = "Запуск Telegram-бота (polling) для привязки chat_id"

    def handle(self, *args: object, **options: object) -> None:
        """Основной цикл опроса Telegram Bot API.

        Args:
            *args: Позиционные аргументы Django.
            **options: Опции команды.
        """
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            self.stderr.write(self.style.ERROR("Set TELEGRAM_BOT_TOKEN in .env"))
            return

        self.stdout.write(self.style.SUCCESS("Telegram bot polling started (Ctrl+C to stop)"))
        offset: int | None = None

        while True:
            try:
                updates = self._fetch_updates(token, offset)
            except requests.RequestException:
                logger.error("Telegram getUpdates failed")
                time.sleep(5)
                continue

            for update in updates:
                update_id = update.get("update_id")
                if isinstance(update_id, int):
                    offset = update_id + 1
                self._handle_update(update)

            time.sleep(1)

    def _fetch_updates(self, token: str, offset: int | None) -> list[dict[str, Any]]:
        """Загружает новые обновления из Bot API."""
        params: dict[str, Any] = {"timeout": 30}
        if offset is not None:
            params["offset"] = offset

        response = requests.get(
            f"{TELEGRAM_API_BASE}/bot{token}/getUpdates",
            params=params,
            timeout=35,
        )
        response.raise_for_status()
        payload = response.json()
        if not payload.get("ok"):
            logger.error("getUpdates returned ok=false")
            return []
        result = payload.get("result")
        if isinstance(result, list):
            return result
        return []

    def _handle_update(self, update: dict[str, Any]) -> None:
        """Обрабатывает одно входящее сообщение."""
        message = update.get("message")
        if not isinstance(message, dict):
            return

        chat = message.get("chat")
        if not isinstance(chat, dict):
            return

        chat_id = chat.get("id")
        if chat_id is None:
            return

        text = message.get("text")
        if not isinstance(text, str):
            return

        chat_id_str = str(chat_id)
        normalized = text.strip()

        try:
            if normalized.startswith("/start"):
                send_message(chat_id_str, _START_TEXT)
            elif normalized.startswith("/link"):
                self._handle_link_command(chat_id_str, normalized)
        except TelegramServiceError:
            logger.error("Failed to reply in chat_id=%s", chat_id_str)

    def _handle_link_command(self, chat_id: str, text: str) -> None:
        """Разбирает ``/link КОД`` и привязывает chat_id."""
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            send_message(chat_id, "Укажите код: /link ВАШ_КОД")
            return

        code = parts[1].strip()
        reply = redeem_link_code(code, chat_id)
        send_message(chat_id, reply)
