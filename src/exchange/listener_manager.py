import asyncio
import logging
from typing import Callable, Awaitable
from src.db.models import Trader
from src.db.session import get_session
from sqlmodel import select
from .binance_listener import BinanceListener

logger = logging.getLogger(__name__)
RawEventCallback = Callable[[dict], Awaitable[None]]


class ListenerManager:
    """Manages one BinanceListener per active trader."""

    def __init__(self, on_event: RawEventCallback) -> None:
        self.on_event = on_event
        self._listeners: dict[int, BinanceListener] = {}

    async def start_all(self) -> None:
        async for session in get_session():
            result = await session.execute(select(Trader).where(Trader.is_active == True))
            traders = result.scalars().all()

        tasks = []
        for trader in traders:
            listener = BinanceListener(
                trader_id=str(trader.id),
                api_key=trader.binance_api_key,
                api_secret=trader.binance_api_secret,
                on_event=self.on_event,
            )
            self._listeners[trader.id] = listener
            tasks.append(listener.start())
            logger.info("Started listener for trader %d (%s)", trader.id, trader.name)

        await asyncio.gather(*tasks)

    async def stop_all(self) -> None:
        for listener in self._listeners.values():
            await listener.stop()
        self._listeners.clear()
