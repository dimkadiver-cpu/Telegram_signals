import asyncio
import pytest
from datetime import datetime, timezone
from src.events.models import TradeEvent
from src.events.types import EventType, Side
from src.trade_engine.engine import TradeEngine
from src.trade_engine.position import PositionStatus


def make_event(event_type: EventType, size: float = 0.1, price: float = 40000.0) -> TradeEvent:
    return TradeEvent(
        event_type=event_type,
        symbol="BTCUSDT",
        side=Side.LONG,
        size=size,
        price=price,
        timestamp=datetime.now(tz=timezone.utc),
        trader_id="trader_1",
    )


def test_open_position():
    engine = TradeEngine()
    pos = asyncio.run(engine.process_event(make_event(EventType.OPEN, size=0.1, price=40000)))
    assert pos.size == 0.1
    assert pos.avg_entry == 40000
    assert pos.status == PositionStatus.OPEN


def test_open_then_add():
    engine = TradeEngine()
    asyncio.run(engine.process_event(make_event(EventType.OPEN, size=0.1, price=40000)))
    pos = asyncio.run(engine.process_event(make_event(EventType.ADD, size=0.1, price=42000)))
    assert pos.size == 0.2
    assert pos.avg_entry == 41000.0


def test_open_then_close():
    engine = TradeEngine()
    asyncio.run(engine.process_event(make_event(EventType.OPEN, size=0.1, price=40000)))
    pos = asyncio.run(engine.process_event(make_event(EventType.CLOSE, size=0.1, price=45000)))
    assert pos.status == PositionStatus.CLOSED
    assert pos.realized_pnl == pytest.approx(500.0)


def test_reduce_position():
    engine = TradeEngine()
    asyncio.run(engine.process_event(make_event(EventType.OPEN, size=0.2, price=40000)))
    pos = asyncio.run(engine.process_event(make_event(EventType.REDUCE, size=0.1, price=40000)))
    assert pos.size == 0.1
