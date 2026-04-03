"""Unit tests for BybitListener."""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def mock_ccxtpro_bybit():
    """Patch ccxt.pro.bybit so no real network calls are made."""
    exchange = MagicMock()
    exchange.watch_orders = AsyncMock()
    exchange.close = AsyncMock()
    exchange.set_sandbox_mode = MagicMock()
    with patch("src.exchange.bybit_listener.ccxtpro") as mock_pro:
        mock_pro.bybit.return_value = exchange
        yield exchange


@pytest.mark.asyncio
async def test_bybit_listener_calls_on_event(mock_ccxtpro_bybit):
    """watch_orders result should be forwarded to on_event with trader_id and _source."""
    from src.exchange.bybit_listener import BybitListener

    received = []

    async def on_event(order):
        received.append(order)

    order_payload = [{"symbol": "BTC/USDT:USDT", "side": "buy", "status": "closed"}]

    call_count = 0

    async def fake_watch_orders():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return order_payload
        # Second call: stop the listener so the loop exits
        listener._running = False
        return []

    mock_ccxtpro_bybit.watch_orders.side_effect = fake_watch_orders

    listener = BybitListener(
        trader_id="7",
        api_key="key",
        api_secret="secret",
        on_event=on_event,
    )

    await listener.start()

    assert len(received) == 1
    assert received[0]["trader_id"] == "7"
    assert received[0]["_source"] == "bybit"
    assert received[0]["symbol"] == "BTC/USDT:USDT"


@pytest.mark.asyncio
async def test_bybit_listener_stop(mock_ccxtpro_bybit):
    """stop() should set _running=False and close the exchange."""
    from src.exchange.bybit_listener import BybitListener

    async def on_event(order):
        pass

    # watch_orders blocks until stop() is called from outside
    async def blocking_watch():
        # simulate waiting; listener.stop() will be called concurrently
        await asyncio.sleep(0.05)
        return []

    mock_ccxtpro_bybit.watch_orders.side_effect = blocking_watch

    listener = BybitListener(
        trader_id="8",
        api_key="key",
        api_secret="secret",
        on_event=on_event,
    )

    async def stop_after_start():
        await asyncio.sleep(0.01)
        await listener.stop()

    await asyncio.gather(listener.start(), stop_after_start())

    assert listener._running is False
    mock_ccxtpro_bybit.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_bybit_listener_testnet_sets_sandbox(mock_ccxtpro_bybit):
    """testnet=True should call set_sandbox_mode(True)."""
    from src.exchange.bybit_listener import BybitListener

    async def on_event(order):
        pass

    mock_ccxtpro_bybit.watch_orders.side_effect = AsyncMock(return_value=[])

    listener = BybitListener(
        trader_id="9",
        api_key="key",
        api_secret="secret",
        on_event=on_event,
        testnet=True,
    )
    mock_ccxtpro_bybit.set_sandbox_mode.assert_called_once_with(True)


@pytest.mark.asyncio
async def test_bybit_listener_reconnects_on_error(mock_ccxtpro_bybit):
    """Listener should reconnect after a transient error, not crash."""
    from src.exchange.bybit_listener import BybitListener

    received = []

    async def on_event(order):
        received.append(order)

    call_count = 0

    async def flaky_watch():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise ConnectionError("ws dropped")
        if call_count == 2:
            return [{"symbol": "ETH/USDT:USDT", "side": "sell", "status": "closed"}]
        listener._running = False
        return []

    mock_ccxtpro_bybit.watch_orders.side_effect = flaky_watch

    listener = BybitListener(
        trader_id="10",
        api_key="key",
        api_secret="secret",
        on_event=on_event,
    )

    # Patch asyncio.sleep to avoid real delay in tests
    with patch("src.exchange.bybit_listener.asyncio.sleep", new_callable=AsyncMock):
        await listener.start()

    assert len(received) == 1
    assert received[0]["symbol"] == "ETH/USDT:USDT"
