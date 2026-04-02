import logging
from aiogram import Bot
from src.db.models import TelegramDraft, DraftStatus, Trader
from src.db.session import get_session

logger = logging.getLogger(__name__)


class MessageDispatcher:
    """Sends approved drafts to the trader's target Telegram channel."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def dispatch(self, draft: TelegramDraft) -> None:
        async for session in get_session():
            trader = await session.get(Trader, draft.trader_id)
            channel = trader.telegram_channel_id if trader else draft.chat_id

        try:
            await self.bot.send_message(
                chat_id=channel,
                text=draft.message_text,
                parse_mode="Markdown",
            )
            async for session in get_session():
                db_draft = await session.get(TelegramDraft, draft.id)
                if db_draft:
                    db_draft.status = DraftStatus.SENT
                    await session.commit()
            logger.info("Draft %d dispatched to channel %s", draft.id, channel)
        except Exception as exc:
            logger.error("Failed to dispatch draft %d: %s", draft.id, exc)
            raise
