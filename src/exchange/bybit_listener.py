import asyncio
import logging
import ccxt.pro as ccxtpro
from .base_listener import BaseListener, RawEventCallback

logger = logging.getLogger(__name__)


class BybitListener(BaseListener):
    """Listens to Bybit order updates via CCXT Pro WebSocket (watch_orders)."""

    def __init__(self, trader_id: str, api_key: str, api_secret: str,
                 on_event: RawEventCallback, testnet: bool = False) -> None:
        super().__init__(trader_id, on_event)
        self._exchange = ccxtpro.bybit({
            "apiKey": api_key,
            "secret": api_secret,
            "enableRateLimit": True,
        })
        if testnet:
            self._exchange.set_sandbox_mode(True)

    async def start(self) -> None:
        self._running = True
        backoff = 1
        while self._running:
            try:
                orders = await self._exchange.watch_orders()
                backoff = 1
                for order in orders:
                    if not self._running:
                        break
                    order["trader_id"] = self.trader_id
                    order["_source"] = "bybit"
                    await self.on_event(order)
            except Exception as exc:
                if not self._running:
                    break
                logger.warning(
                    "Bybit WS disconnected (%s). Reconnecting in %ds.", exc, backoff
                )
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 60)

    async def stop(self) -> None:
        self._running = False
        await self._exchange.close()
