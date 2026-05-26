"""Отправка сообщений через Telegram Bot API."""

import logging
import os

import requests

logger = logging.getLogger(__name__)

TELEGRAM_API_BASE = "https://api.telegram.org"


class TelegramServiceError(Exception):
    """Ошибка вызова Telegram Bot API без раскрытия токена клиенту."""


def send_message(chat_id: str, text: str) -> None:
    """Отправляет текстовое сообщение в чат Telegram.

    Args:
        chat_id: Идентификатор чата получателя.
        text: Текст сообщения.

    Raises:
        TelegramServiceError: Если токен не задан или Bot API вернул ошибку.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN is not configured")
        raise TelegramServiceError("Telegram is not configured")

    try:
        response = requests.post(
            f"{TELEGRAM_API_BASE}/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=10,
        )
    except requests.RequestException as exc:
        logger.exception("Telegram request failed for chat_id=%s", chat_id)
        raise TelegramServiceError("Failed to send Telegram message") from exc

    if not response.ok:
        logger.error(
            "Telegram API error status=%s chat_id=%s",
            response.status_code,
            chat_id,
        )
        raise TelegramServiceError("Failed to send Telegram message")
