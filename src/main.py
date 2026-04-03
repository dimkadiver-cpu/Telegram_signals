import asyncio
import logging
import signal
from src.config import Settings
from src.db.session import init_db, create_tables
from src.db.models import Trader
from src.db.session import get_session
from src.db.position_repository import PositionRepository
from src.exchange.listener_manager import ListenerManager
from src.events.normalizer import EventNormalizer
from src.trade_engine.engine import TradeEngine
from src.metrics.calculator import MetricCalculator
from src.metrics.config import RiskConfig
from src.templates.renderer import TemplateRenderer
from src.templates.store import TemplateStore
from src.telegram.bot import init_bot
from src.telegram.draft_manager import DraftManager
from src.telegram.handlers import router as telegram_router
from src.dispatcher.dispatcher import MessageDispatcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = Settings()


def _resolve_auto_approve_set(trader: Trader, global_setting: str) -> set[str]:
    """Return the set of EventType values that bypass review for this trader."""
    raw = (trader.auto_approve_events or "").strip() or global_setting.strip()
    return {v.strip().upper() for v in raw.split(",") if v.strip()}


async def build_pipeline(
    bot,
    draft_manager: DraftManager,
    dispatcher: MessageDispatcher,
    position_repo: PositionRepository,
) -> tuple:
    """Wire normalizer → engine → metrics → template → draft/dispatch.

    Returns (on_raw_event callback, TradeEngine) so the caller can restore
    persisted positions into the engine before starting listeners.
    """
    normalizer = EventNormalizer()
    engine = TradeEngine(position_repo=position_repo)
    calculator = MetricCalculator()
    renderer = TemplateRenderer()
    template_store = TemplateStore()

    async def get_trader(trader_id: int) -> Trader | None:
        async for session in get_session():
            return await session.get(Trader, trader_id)
        return None

    async def on_raw_event(raw: dict) -> None:
        event = normalizer.normalize(raw, source="binance")
        if event is None:
            return
        try:
            trader_id = int(event.trader_id)
        except (TypeError, ValueError):
            logger.warning("Invalid trader_id in event: %s", event.trader_id)
            return

        trader = await get_trader(trader_id)
        if trader is None or not trader.is_active:
            logger.warning("Skipping event for unknown/inactive trader_id=%s", trader_id)
            return

        position = await engine.process_event(event)
        risk_config = RiskConfig(
            capital_usd=settings.risk_capital_usd,
            risk_pct=settings.risk_pct,
        )
        metrics = calculator.calculate(
            position, risk_config, current_price=event.price, event_type=event.event_type
        )
        custom_template = await template_store.get_template(trader.id, event.event_type)
        message_text = renderer.render(
            event.event_type,
            position,
            metrics,
            custom_template=custom_template,
            event=event,
        )

        auto_approve_set = _resolve_auto_approve_set(trader, settings.auto_approve_events)
        if event.event_type.value in auto_approve_set:
            draft = await draft_manager.create_draft_only(
                trader_id=trader.id,
                review_chat_id=trader.telegram_review_chat_id,
                message_text=message_text,
            )
            await dispatcher.dispatch(draft)
        else:
            await draft_manager.send_draft(
                trader_id=trader.id,
                review_chat_id=trader.telegram_review_chat_id,
                message_text=message_text,
            )

    return on_raw_event, engine


async def main() -> None:
    init_db(settings.database_url)
    await create_tables()

    bot, dp = init_bot(settings.telegram_bot_token)
    dp.include_router(telegram_router)

    dispatcher = MessageDispatcher(bot)
    draft_manager = DraftManager(bot)

    position_repo = PositionRepository()
    on_event, engine = await build_pipeline(bot, draft_manager, dispatcher, position_repo)
    listener_manager = ListenerManager(on_event=on_event)

    open_positions = await position_repo.load_open_positions()
    if open_positions:
        engine.restore_positions(open_positions)

    telegram_router.data["dispatcher"] = dispatcher
    telegram_router.data["listener_manager"] = listener_manager

    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    logger.info("Starting Telegram Signals system...")
    try:
        await asyncio.gather(
            listener_manager.start_all(),
            dp.start_polling(bot),
        )
    finally:
        await listener_manager.stop_all()
        await bot.session.close()
        logger.info("Shutdown complete.")


if __name__ == "__main__":
    asyncio.run(main())
