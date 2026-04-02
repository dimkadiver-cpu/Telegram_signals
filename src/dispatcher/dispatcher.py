import asyncio
import logging
from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter
from src.db.models import TelegramDraft, DraftStatus, Trader
from src.db.session import get_session

logger = logging.getLogger(__name__)

_MAX_RETRIES = 5


class MessageDispatcher:
    """Sends approved drafts to the trader's target Telegram channel."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def dispatch(self, draft: TelegramDraft) -> None:
        async for session in get_session():
            trader = await session.get(Trader, draft.trader_id)
            channel = trader.telegram_channel_id if trader else draft.chat_id

        backoff = 1
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                await self.bot.send_message(
                    chat_id=channel,
                    text=draft.message_text,
                    parse_mode="Markdown",
                )
                break
            except TelegramRetryAfter as exc:
                wait = exc.retry_after if exc.retry_after else backoff
                logger.warning(
                    "Telegram 429 on draft %d (attempt %d/%d). Retrying in %ds.",
                    draft.id, attempt, _MAX_RETRIES, wait,
                )
                if attempt == _MAX_RETRIES:
                    logger.error("Exhausted retries for draft %d.", draft.id)
                    raise
                await asyncio.sleep(wait)
                backoff = min(backoff * 2, 60)
            except Exception as exc:
                logger.error("Failed to dispatch draft %d: %s", draft.id, exc)
                raise

        async for session in get_session():
            db_draft = await session.get(TelegramDraft, draft.id)
            if db_draft:
                db_draft.status = DraftStatus.SENT
                await session.commit()
        logger.info("Draft %d dispatched to channel %s", draft.id, channel)
