"""F5-09 – Test longevity stream Binance: il keepalive viene chiamato durante sessioni lunghe."""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call
from src.exchange.binance_listener import BinanceListener, _KEEPALIVE_INTERVAL


def _make_listener(on_event=None) -> BinanceListener:
    if on_event is None:
        on_event = AsyncMock()
    return BinanceListener(
        trader_id="trader_1",
        api_key="key",
        api_secret="secret",
        on_event=on_event,
    )


@pytest.mark.asyncio
async def test_keepalive_called_at_interval():
    """_keepalive_loop renews the listenKey after the configured interval."""
    listener = _make_listener()
    listener._running = True

    new_key = "new_listen_key_456"
    client_mock = AsyncMock()
    client_mock.futures_stream_get_listen_key = AsyncMock(return_value=new_key)
    listener._client = client_mock

    # Patch sleep so the first call returns immediately, triggering one renewal
    sleep_calls = []

    async def fast_sleep(seconds):
        sleep_calls.append(seconds)
        listener._running = False  # Stop after first renewal

    with patch("src.exchange.binance_listener.asyncio.sleep", side_effect=fast_sleep):
        await listener._keepalive_loop()

    client_mock.futures_stream_get_listen_key.assert_awaited_once()
    assert listener._listen_key == new_key
    assert sleep_calls == [_KEEPALIVE_INTERVAL]


@pytest.mark.asyncio
async def test_keepalive_loop_cancelled_gracefully():
    """_keepalive_loop exits cleanly when cancelled."""
    listener = _make_listener()
    listener._running = True

    async def blocking_sleep(seconds):
        raise asyncio.CancelledError()

    client_mock = AsyncMock()
    listener._client = client_mock

    with patch("src.exchange.binance_listener.asyncio.sleep", side_effect=blocking_sleep):
        # Should not raise
        await listener._keepalive_loop()

    client_mock.futures_stream_get_listen_key.assert_not_awaited()


@pytest.mark.asyncio
async def test_keepalive_survives_renewal_error():
    """_keepalive_loop logs and continues after a renewal error (does not crash)."""
    listener = _make_listener()
    listener._running = True

    call_count = 0

    async def flaky_get_listen_key():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise ConnectionError("temporary failure")
        return "recovered_key"

    client_mock = AsyncMock()
    client_mock.futures_stream_get_listen_key = flaky_get_listen_key
    listener._client = client_mock

    sleep_count = [0]

    async def limited_sleep(seconds):
        sleep_count[0] += 1
        if sleep_count[0] >= 2:
            listener._running = False

    with patch("src.exchange.binance_listener.asyncio.sleep", side_effect=limited_sleep):
        await listener._keepalive_loop()

    # Second attempt should have succeeded
    assert listener._listen_key == "recovered_key"


@pytest.mark.asyncio
async def test_keepalive_task_started_on_start():
    """start() creates the keepalive task before starting the WebSocket loop."""
    listener = _make_listener()

    client_mock = AsyncMock()
    client_mock.futures_stream_get_listen_key = AsyncMock(return_value="initial_key")
    socket_manager_mock = MagicMock()

    # Make the WS stream raise immediately so start() returns
    cm = AsyncMock()
    cm.__aenter__ = AsyncMock(return_value=AsyncMock(__aiter__=MagicMock(return_value=iter([]))))
    cm.__aexit__ = AsyncMock(return_value=False)
    socket_manager_mock.futures_user_socket = MagicMock(return_value=cm)

    with patch("src.exchange.binance_listener.AsyncClient.create", return_value=client_mock), \
         patch("src.exchange.binance_listener.BinanceSocketManager", return_value=socket_manager_mock), \
         patch.object(listener, "_keepalive_loop", new_callable=AsyncMock) as mock_kl:

        listener._running = False  # Prevent infinite loop in _listen_with_reconnect
        await listener.start()

    mock_kl.assert_awaited()
    assert listener._listen_key == "initial_key"
