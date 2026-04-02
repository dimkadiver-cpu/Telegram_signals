import logging
from aiogram import Bot
from src.db.models import TelegramDraft, DraftStatus
from src.db.session import get_session
from .keyboards import draft_keyboard

logger = logging.getLogger(__name__)


class DraftManager:
    """Creates and sends review drafts to the trader's review chat."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def send_draft(self, trader_id: int, review_chat_id: str,
                         message_text: str, trade_id: int | None = None) -> TelegramDraft:
        async for session in get_session():
            draft = TelegramDraft(
                trader_id=trader_id,
                trade_id=trade_id,
                chat_id=review_chat_id,
                message_text=message_text,
                status=DraftStatus.PENDING,
            )
            session.add(draft)
            await session.commit()
            await session.refresh(draft)

            sent = await self.bot.send_message(
                chat_id=review_chat_id,
                text=message_text,
                reply_markup=draft_keyboard(draft.id),
                parse_mode="Markdown",
            )
            draft.telegram_message_id = sent.message_id
            await session.commit()
            logger.info("Draft %d sent to chat %s", draft.id, review_chat_id)
            return draft
