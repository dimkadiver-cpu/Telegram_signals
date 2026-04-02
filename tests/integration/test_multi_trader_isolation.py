import asyncio
from datetime import datetime

from src.db.models import DraftStatus, TelegramDraft, Trader, TraderTemplate
from src.db.session import create_tables, get_session, init_db
from src.dispatcher.dispatcher import MessageDispatcher
from src.events.models import TradeEvent
from src.events.types import EventType, Side
from src.templates.renderer import TemplateRenderer
from src.templates.store import TemplateStore
from src.trade_engine.engine import TradeEngine


class BotSpy:
    def __init__(self) -> None:
        self.sent_messages: list[dict] = []

    async def send_message(self, chat_id: str, text: str, parse_mode: str | None = None):
        self.sent_messages.append(
            {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
        )


def make_event(trader_id: str, price: float) -> TradeEvent:
    return TradeEvent(
        event_type=EventType.OPEN,
        symbol="BTCUSDT",
        side=Side.LONG,
        size=0.1,
        price=price,
        timestamp=datetime.utcnow(),
        trader_id=trader_id,
    )


def test_trade_engine_keeps_positions_isolated_by_trader():
    engine = TradeEngine()

    pos_t1 = asyncio.run(engine.process_event(make_event("1", 40_000.0)))
    pos_t2 = asyncio.run(engine.process_event(make_event("2", 41_000.0)))

    assert pos_t1.avg_entry == 40_000.0
    assert pos_t2.avg_entry == 41_000.0
    assert engine.get_position("1", "BTCUSDT").avg_entry == 40_000.0
    assert engine.get_position("2", "BTCUSDT").avg_entry == 41_000.0


def test_template_store_loads_trader_specific_template(tmp_path):
    async def run() -> None:
        db_path = tmp_path / "multi_trader_templates.db"
        init_db(f"sqlite+aiosqlite:///{db_path}")
        await create_tables()

        async for session in get_session():
            session.add(
                Trader(
                    id=1,
                    name="Trader One",
                    binance_api_key="k1",
                    binance_api_secret="s1",
                    telegram_review_chat_id="review_1",
                    telegram_channel_id="channel_1",
                    is_active=True,
                )
            )
            session.add(
                Trader(
                    id=2,
                    name="Trader Two",
                    binance_api_key="k2",
                    binance_api_secret="s2",
                    telegram_review_chat_id="review_2",
                    telegram_channel_id="channel_2",
                    is_active=True,
                )
            )
            session.add(
                TraderTemplate(
                    trader_id=1,
                    event_type=EventType.OPEN.value,
                    template_text="T1 {{ symbol }}",
                )
            )
            await session.commit()

        store = TemplateStore()
        renderer = TemplateRenderer()

        from src.trade_engine.position import Position

        position = Position(
            trader_id="1",
            symbol="BTCUSDT",
            side=Side.LONG,
            size=0.1,
            avg_entry=40_000.0,
        )
        template_t1 = await store.get_template(1, EventType.OPEN)
        template_t2 = await store.get_template(2, EventType.OPEN)

        rendered_t1 = renderer.render(EventType.OPEN, position, custom_template=template_t1)
        rendered_t2 = renderer.render(EventType.OPEN, position, custom_template=template_t2)

        assert rendered_t1 == "T1 BTCUSDT"
        assert "OPEN" in rendered_t2

    asyncio.run(run())


def test_dispatcher_routes_to_trader_channel(tmp_path):
    async def run() -> None:
        db_path = tmp_path / "multi_trader_dispatch.db"
        init_db(f"sqlite+aiosqlite:///{db_path}")
        await create_tables()

        async for session in get_session():
            session.add(
                Trader(
                    id=10,
                    name="Trader Ten",
                    binance_api_key="k10",
                    binance_api_secret="s10",
                    telegram_review_chat_id="review_10",
                    telegram_channel_id="channel_10",
                    is_active=True,
                )
            )
            draft = TelegramDraft(
                trader_id=10,
                chat_id="review_10",
                message_text="hello",
                status=DraftStatus.APPROVED,
            )
            session.add(draft)
            await session.commit()
            await session.refresh(draft)

        bot = BotSpy()
        dispatcher = MessageDispatcher(bot)
        await dispatcher.dispatch(draft)

        assert bot.sent_messages[0]["chat_id"] == "channel_10"

    asyncio.run(run())
