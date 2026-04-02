import asyncio
import logging
from binance import AsyncClient, BinanceSocketManager
from .base_listener import BaseListener, RawEventCallback

logger = logging.getLogger(__name__)


class BinanceListener(BaseListener):
    """Listens to Binance User Data Stream (Futures) via official SDK."""

    def __init__(self, trader_id: str, api_key: str, api_secret: str,
                 on_event: RawEventCallback, testnet: bool = False) -> None:
        super().__init__(trader_id, on_event)
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self._client: AsyncClient | None = None
        self._socket_manager: BinanceSocketManager | None = None

    async def start(self) -> None:
        self._running = True
        self._client = await AsyncClient.create(
            self.api_key, self.api_secret, testnet=self.testnet
        )
        self._socket_manager = BinanceSocketManager(self._client)
        await self._listen_with_reconnect()

    async def stop(self) -> None:
        self._running = False
        if self._client:
            await self._client.close_connection()

    async def _listen_with_reconnect(self) -> None:
        backoff = 1
        while self._running:
            try:
                async with self._socket_manager.futures_user_socket() as stream:
                    backoff = 1
                    async for raw_event in stream:
                        if not self._running:
                            break
                        await self.on_event({**raw_event, "trader_id": self.trader_id})
            except Exception as exc:
                if not self._running:
                    break
                logger.warning("Binance WS disconnected (%s). Reconnecting in %ds.", exc, backoff)
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 60)
