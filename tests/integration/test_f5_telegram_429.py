"""F5-08 – Test resilienza retry: il dispatcher gestisce errori Telegram 429 con backoff."""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call
from aiogram.exceptions import TelegramRetryAfter
from src.dispatcher.dispatcher import MessageDispatcher
from src.db.models import TelegramDraft, DraftStatus


def _make_draft(draft_id: int = 1, trader_id: int = 10) -> TelegramDraft:
    draft = MagicMock(spec=TelegramDraft)
    draft.id = draft_id
    draft.trader_id = trader_id
    draft.message_text = "Test messaggio"
    draft.chat_id = "channel_fallback"
    return draft


def _make_bot(side_effects):
    """Return a mock Bot whose send_message raises the given side_effects in sequence."""
    bot = MagicMock()
    bot.send_message = AsyncMock(side_effect=side_effects)
    return bot


def _make_retry_after(seconds: int = 5) -> TelegramRetryAfter:
    exc = MagicMock(spec=TelegramRetryAfter)
    exc.retry_after = seconds
    return exc


@pytest.mark.asyncio
async def test_dispatch_succeeds_after_one_429():
    """Dispatcher retries and succeeds after a single 429."""
    bot = _make_bot([_make_retry_after(0), None])

    with patch("src.dispatcher.dispatcher.get_session") as mock_session, \
         patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:

        # Session mock: first call returns trader, subsequent calls return draft
        trader_mock = MagicMock()
        trader_mock.telegram_channel_id = "channel_123"

        draft_mock = MagicMock(spec=TelegramDraft)

        session_mock = AsyncMock()
        session_mock.get = AsyncMock(side_effect=[trader_mock, draft_mock])
        mock_session.return_value.__aiter__ = MagicMock(
            return_value=iter([session_mock])
        )

        async def mock_get_session():
            yield session_mock

        mock_session.side_effect = None
        mock_session.return_value = mock_get_session()

        # Use a fresh async generator each call
        call_count = [0]
        async def dynamic_get_session():
            call_count[0] += 1
            yield session_mock

        mock_session.side_effect = lambda: dynamic_get_session()

        dispatcher = MessageDispatcher(bot)
        draft = _make_draft()
        await dispatcher.dispatch(draft)

    assert bot.send_message.call_count == 2
    mock_sleep.assert_awaited_once_with(0)


@pytest.mark.asyncio
async def test_dispatch_exhausts_retries():
    """Dispatcher raises after _MAX_RETRIES failed attempts."""
    from src.dispatcher.dispatcher import _MAX_RETRIES
    retry_exc = _make_retry_after(0)
    bot = _make_bot([retry_exc] * _MAX_RETRIES)

    with patch("src.dispatcher.dispatcher.get_session") as mock_session, \
         patch("asyncio.sleep", new_callable=AsyncMock):

        trader_mock = MagicMock()
        trader_mock.telegram_channel_id = "channel_123"
        session_mock = AsyncMock()
        session_mock.get = AsyncMock(return_value=trader_mock)

        async def dynamic_get_session():
            yield session_mock

        mock_session.side_effect = lambda: dynamic_get_session()

        dispatcher = MessageDispatcher(bot)
        draft = _make_draft()
        with pytest.raises(TelegramRetryAfter):
            await dispatcher.dispatch(draft)

    assert bot.send_message.call_count == _MAX_RETRIES


@pytest.mark.asyncio
async def test_dispatch_non_429_raises_immediately():
    """Dispatcher does not retry on non-429 exceptions."""
    bot = _make_bot([ValueError("network error")])

    with patch("src.dispatcher.dispatcher.get_session") as mock_session, \
         patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:

        trader_mock = MagicMock()
        trader_mock.telegram_channel_id = "channel_123"
        session_mock = AsyncMock()
        session_mock.get = AsyncMock(return_value=trader_mock)

        async def dynamic_get_session():
            yield session_mock

        mock_session.side_effect = lambda: dynamic_get_session()

        dispatcher = MessageDispatcher(bot)
        draft = _make_draft()
        with pytest.raises(ValueError):
            await dispatcher.dispatch(draft)

    assert bot.send_message.call_count == 1
    mock_sleep.assert_not_awaited()
