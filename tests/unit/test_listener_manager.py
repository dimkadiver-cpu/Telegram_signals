import asyncio

from src.db.models import Trader
from src.exchange.listener_manager import ListenerManager


class FakeListener:
    def __init__(self, trader_id: str, api_key: str, api_secret: str, on_event):
        self.trader_id = trader_id
        self.on_event = on_event
        self.started = False
        self.stopped = False

    async def start(self) -> None:
        self.started = True
        while not self.stopped:
            await asyncio.sleep(0.01)

    async def stop(self) -> None:
        self.stopped = True


def test_listener_manager_add_and_remove_trader(monkeypatch):
    async def run() -> None:
        monkeypatch.setattr("src.exchange.listener_manager.BinanceListener", FakeListener)

        async def on_event(_: dict) -> None:
            return None

        manager = ListenerManager(on_event=on_event)

        trader = Trader(
            id=1,
            name="t1",
            binance_api_key="k1",
            binance_api_secret="s1",
            telegram_review_chat_id="r1",
            telegram_channel_id="c1",
            is_active=True,
        )

        await manager.add_trader(trader)
        assert 1 in manager._listeners
        assert 1 in manager._tasks

        await asyncio.sleep(0.02)
        await manager.remove_trader(1)

        assert 1 not in manager._listeners
        assert 1 not in manager._tasks

    asyncio.run(run())


def test_listener_manager_skip_inactive_trader(monkeypatch):
    async def run() -> None:
        monkeypatch.setattr("src.exchange.listener_manager.BinanceListener", FakeListener)

        async def on_event(_: dict) -> None:
            return None

        manager = ListenerManager(on_event=on_event)
        trader = Trader(
            id=2,
            name="t2",
            binance_api_key="k2",
            binance_api_secret="s2",
            telegram_review_chat_id="r2",
            telegram_channel_id="c2",
            is_active=False,
        )

        await manager.add_trader(trader)
        assert manager._listeners == {}
        assert manager._tasks == {}

    asyncio.run(run())
