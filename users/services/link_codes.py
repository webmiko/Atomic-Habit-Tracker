"""Одноразовые коды привязки Telegram."""

from datetime import timedelta

from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.crypto import get_random_string

from users.models import TelegramLinkCode, User

CODE_TTL_MINUTES = 15
CODE_LENGTH = 8
_CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def create_link_code(user: User) -> TelegramLinkCode:
    """Создаёт одноразовый код привязки для пользователя.

    Старые неиспользованные коды этого пользователя удаляются.

    Args:
        user: Владелец кода.

    Returns:
        Новая запись TelegramLinkCode с полем expires_at.

    Raises:
        RuntimeError: Если не удалось сгенерировать уникальный код.
    """
    TelegramLinkCode.objects.filter(user=user).delete()
    expires_at = timezone.now() + timedelta(minutes=CODE_TTL_MINUTES)

    for _ in range(10):
        code = get_random_string(CODE_LENGTH, allowed_chars=_CODE_ALPHABET)
        if TelegramLinkCode.objects.filter(code=code).exists():
            continue
        link: TelegramLinkCode = TelegramLinkCode.objects.create(
            user=user,
            code=code,
            expires_at=expires_at,
        )
        return link

    raise RuntimeError("Could not generate unique Telegram link code")


def redeem_link_code(code: str, chat_id: str) -> str:
    """Привязывает chat_id к пользователю по одноразовому коду.

    Args:
        code: Код из API (регистр не важен).
        chat_id: Идентификатор чата из Telegram.

    Returns:
        Текст ответа для пользователя в боте.
    """
    normalized = code.strip().upper()
    if not normalized:
        return "Укажите код: /link ВАШ_КОД"

    try:
        link = TelegramLinkCode.objects.select_related("user").get(code=normalized)
    except TelegramLinkCode.DoesNotExist:
        return "Код не найден. Запросите новый в настройках приложения."

    if link.expires_at < timezone.now():
        link.delete()
        return "Код истёк. Запросите новый в настройках приложения."

    user = link.user
    chat_id_str = str(chat_id)

    if User.objects.filter(telegram_chat_id=chat_id_str).exclude(pk=user.pk).exists():
        return "Этот Telegram уже привязан к другому аккаунту."

    try:
        with transaction.atomic():
            user.telegram_chat_id = chat_id_str
            user.save(update_fields=["telegram_chat_id"])
            link.delete()
    except IntegrityError:
        return "Этот Telegram уже привязан к другому аккаунту."

    return "Telegram привязан. Включите оповещения в Telegram в настройках приложения (notify_by_telegram)."
