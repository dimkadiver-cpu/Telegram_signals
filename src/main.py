import asyncio
import logging
import signal
from src.config import Settings
from src.db.session import init_db, create_tables
from src.db.models import Trader
from src.db.session import get_session
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


async def build_pipeline(bot, draft_manager: DraftManager) -> None:
    """Wire normalizer → engine → metrics → template → draft."""
    normalizer = EventNormalizer()
    engine = TradeEngine()
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
        metrics = calculator.calculate(position, risk_config, current_price=event.price)
        custom_template = await template_store.get_template(trader.id, event.event_type)
        message_text = renderer.render(
            event.event_type,
            position,
            metrics,
            custom_template=custom_template,
        )
        await draft_manager.send_draft(
            trader_id=trader.id,
            review_chat_id=trader.telegram_review_chat_id,
            message_text=message_text,
        )

    return on_raw_event


async def main() -> None:
    init_db(settings.database_url)
    await create_tables()

    bot, dp = init_bot(settings.telegram_bot_token)
    dp.include_router(telegram_router)

    dispatcher = MessageDispatcher(bot)
    draft_manager = DraftManager(bot)

    on_event = await build_pipeline(bot, draft_manager)
    listener_manager = ListenerManager(on_event=on_event)

    telegram_router.data["dispatcher"] = dispatcher

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
