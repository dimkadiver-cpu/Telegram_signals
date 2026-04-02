import ccxt.async_support as ccxt
from typing import Any


class CCXTClient:
    """REST client via CCXT for market data and position snapshots."""

    def __init__(self, exchange_id: str, api_key: str, api_secret: str,
                 sandbox: bool = False) -> None:
        exchange_class = getattr(ccxt, exchange_id)
        self._exchange: ccxt.Exchange = exchange_class({
            "apiKey": api_key,
            "secret": api_secret,
            "enableRateLimit": True,
        })
        if sandbox:
            self._exchange.set_sandbox_mode(True)

    async def get_ticker(self, symbol: str) -> dict[str, Any]:
        return await self._exchange.fetch_ticker(symbol)

    async def get_open_positions(self) -> list[dict[str, Any]]:
        return await self._exchange.fetch_positions()

    async def get_order_history(self, symbol: str, limit: int = 50) -> list[dict[str, Any]]:
        return await self._exchange.fetch_orders(symbol, limit=limit)

    async def close(self) -> None:
        await self._exchange.close()
