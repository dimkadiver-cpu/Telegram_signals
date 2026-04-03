import asyncio
import logging
from typing import Callable, Awaitable
from src.db.models import Trader
from src.db.session import get_session
from sqlmodel import select
from .base_listener import BaseListener
from .binance_listener import BinanceListener
from .bybit_listener import BybitListener

logger = logging.getLogger(__name__)
RawEventCallback = Callable[[dict], Awaitable[None]]


class ListenerManager:
    """Manages one listener per active trader, dispatching by exchange type."""

    def __init__(self, on_event: RawEventCallback) -> None:
        self.on_event = on_event
        self._listeners: dict[int, BaseListener] = {}
        self._tasks: dict[int, asyncio.Task] = {}
        self._lock = asyncio.Lock()

    def _create_listener(self, trader: Trader) -> BaseListener:
        exchange = getattr(trader, "exchange", "binance") or "binance"
        if exchange == "bybit":
            return BybitListener(
                trader_id=str(trader.id),
                api_key=trader.binance_api_key,
                api_secret=trader.binance_api_secret,
                on_event=self.on_event,
            )
        # default: binance
        return BinanceListener(
            trader_id=str(trader.id),
            api_key=trader.binance_api_key,
            api_secret=trader.binance_api_secret,
            on_event=self.on_event,
        )

    async def _start_listener(self, trader: Trader) -> None:
        if trader.id is None:
            return
        if trader.id in self._listeners:
            logger.info("Listener already running for trader %d", trader.id)
            return
        listener = self._create_listener(trader)
        self._listeners[trader.id] = listener
        self._tasks[trader.id] = asyncio.create_task(listener.start())
        logger.info("Started listener for trader %d (%s)", trader.id, trader.name)

    async def add_trader(self, trader: Trader) -> None:
        async with self._lock:
            if not trader.is_active:
                logger.info("Skip listener start for inactive trader %s", trader.id)
                return
            await self._start_listener(trader)

    async def remove_trader(self, trader_id: int) -> None:
        async with self._lock:
            listener = self._listeners.pop(trader_id, None)
            task = self._tasks.pop(trader_id, None)
            if listener is None:
                return
            await listener.stop()
            if task:
                try:
                    await task
                except Exception:
                    logger.exception("Listener task ended with error for trader %d", trader_id)
            logger.info("Stopped listener for trader %d", trader_id)

    async def start_all(self) -> None:
        async for session in get_session():
            result = await session.execute(select(Trader).where(Trader.is_active))
            traders = result.scalars().all()

        if not traders:
            logger.warning("No active traders found: exchange listeners not started.")
            return
        for trader in traders:
            await self.add_trader(trader)

    async def stop_all(self) -> None:
        trader_ids = list(self._listeners.keys())
        for trader_id in trader_ids:
            await self.remove_trader(trader_id)
