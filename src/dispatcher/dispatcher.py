import logging
from aiogram import Bot
from src.db.models import TelegramDraft, DraftStatus
from src.db.session import get_session

logger = logging.getLogger(__name__)


class MessageDispatcher:
    """Sends approved drafts to the trader's target Telegram channel."""

    def __init__(self, bot: Bot, target_channel_id: str | None = None) -> None:
        self.bot = bot
        self.target_channel_id = target_channel_id  # per-trader override from DB

    async def dispatch(self, draft: TelegramDraft) -> None:
        channel = self.target_channel_id or draft.chat_id
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
