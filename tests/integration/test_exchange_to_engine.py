"""Integration test: raw Binance event → TradeEngine → Position."""
import asyncio
import pytest
from src.events.normalizer import EventNormalizer
from src.trade_engine.engine import TradeEngine
from src.trade_engine.position import PositionStatus


RAW_OPEN = {
    "e": "ORDER_TRADE_UPDATE",
    "T": 1700000000000,
    "trader_id": "trader_1",
    "o": {
        "s": "BTCUSDT", "S": "BUY", "X": "FILLED",
        "l": "0.1", "L": "40000.0", "R": False, "ps": "BOTH", "i": "o1",
    },
}

RAW_CLOSE = {
    "e": "ORDER_TRADE_UPDATE",
    "T": 1700001000000,
    "trader_id": "trader_1",
    "o": {
        "s": "BTCUSDT", "S": "SELL", "X": "FILLED",
        "l": "0.1", "L": "45000.0", "R": True, "ps": "BOTH", "i": "o2",
    },
}


@pytest.mark.asyncio
async def test_open_and_close_pipeline():
    normalizer = EventNormalizer()
    engine = TradeEngine()

    open_event = normalizer.normalize(RAW_OPEN)
    assert open_event is not None
    pos = await engine.process_event(open_event)
    assert pos.status == PositionStatus.OPEN
    assert pos.size == 0.1

    close_event = normalizer.normalize(RAW_CLOSE)
    assert close_event is not None
    pos = await engine.process_event(close_event)
    assert pos.status == PositionStatus.CLOSED
    assert pos.realized_pnl == pytest.approx(500.0)
