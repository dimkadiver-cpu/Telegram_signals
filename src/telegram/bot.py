import re
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

logger = logging.getLogger(__name__)

# Telegram bot tokens follow the pattern: {bot_id}:{alphanumeric_secret}
_TOKEN_RE = re.compile(r"^\d+:[A-Za-z0-9_-]{35,}$")

_bot: Bot | None = None
_dispatcher: Dispatcher | None = None


def get_bot() -> Bot:
    if _bot is None:
        raise RuntimeError("Bot not initialized. Call init_bot() first.")
    return _bot


def get_dispatcher() -> Dispatcher:
    if _dispatcher is None:
        raise RuntimeError("Dispatcher not initialized. Call init_bot() first.")
    return _dispatcher


def _validate_token_format(token: str) -> None:
    if not token or not _TOKEN_RE.match(token):
        raise ValueError(
            "Invalid Telegram bot token format. "
            "Expected '<bot_id>:<35+ char secret>', got: "
            f"'{token[:10]}...'" if token else "empty string"
        )


def init_bot(token: str) -> tuple[Bot, Dispatcher]:
    global _bot, _dispatcher
    _validate_token_format(token)
    _bot = Bot(token=token)
    _dispatcher = Dispatcher(storage=MemoryStorage())
    logger.info("Telegram bot initialized (token format OK).")
    return _bot, _dispatcher
