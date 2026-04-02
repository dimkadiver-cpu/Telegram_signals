import asyncio
import logging
import signal
from src.config import Settings
from src.db.session import init_db, create_tables
from src.exchange.binance_listener import BinanceListener
from src.exchange.listener_manager import ListenerManager
from src.events.normalizer import EventNormalizer
from src.trade_engine.engine import TradeEngine
from src.metrics.calculator import MetricCalculator
from src.metrics.config import RiskConfig
from src.templates.renderer import TemplateRenderer
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
    risk_config = RiskConfig(
        capital_usd=settings.risk_capital_usd,
        risk_pct=settings.risk_pct,
    )
    renderer = TemplateRenderer()

    async def on_raw_event(raw: dict) -> None:
        event = normalizer.normalize(raw, source="binance")
        if event is None:
            return
        position = await engine.process_event(event)
        metrics = calculator.calculate(position, risk_config, current_price=event.price)
        message_text = renderer.render(event.event_type, position, metrics)
        await draft_manager.send_draft(
            trader_id=event.trader_id,
            review_chat_id=settings.telegram_review_chat_id,
            message_text=message_text,
        )

    return on_raw_event


async def main() -> None:
    init_db(settings.database_url)
    await create_tables()

    bot, dp = init_bot(settings.telegram_bot_token)
    dp.include_router(telegram_router)

    dispatcher = MessageDispatcher(bot, target_channel_id=settings.telegram_channel_id)
    draft_manager = DraftManager(bot)

    on_event = await build_pipeline(bot, draft_manager)

    listener = BinanceListener(
        trader_id="default",
        api_key=settings.binance_api_key,
        api_secret=settings.binance_api_secret,
        on_event=on_event,
        testnet=settings.binance_testnet,
    )

    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    logger.info("Starting Telegram Signals system...")
    try:
        await asyncio.gather(
            listener.start(),
            dp.start_polling(bot),
        )
    finally:
        await listener.stop()
        await bot.session.close()
        logger.info("Shutdown complete.")


if __name__ == "__main__":
    asyncio.run(main())
