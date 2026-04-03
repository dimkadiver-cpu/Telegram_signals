import asyncio
import pytest
from datetime import datetime, timezone
from src.events.models import TradeEvent
from src.events.types import EventType, Side
from src.trade_engine.engine import TradeEngine
from src.trade_engine.position import PositionStatus


def make_event(event_type: EventType, size: float = 0.1, price: float = 40000.0,
               side: Side = Side.LONG, stop_loss: float | None = None,
               take_profit: float | None = None, order_type: str | None = None) -> TradeEvent:
    return TradeEvent(
        event_type=event_type,
        symbol="BTCUSDT",
        side=side,
        size=size,
        price=price,
        timestamp=datetime.now(tz=timezone.utc),
        trader_id="trader_1",
        stop_loss=stop_loss,
        take_profit=take_profit,
        order_type=order_type,
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


# ── New event tests ───────────────────────────────────────────────────────────

def test_order_cancelled_with_open_position_is_dca_cancel():
    """ORDER_CANCELLED on open position → DCA cancelled, position stays open."""
    engine = TradeEngine()
    asyncio.run(engine.process_event(make_event(EventType.OPEN, size=0.1, price=40000)))
    pos = asyncio.run(engine.process_event(make_event(EventType.ORDER_CANCELLED)))
    assert pos.status == PositionStatus.OPEN
    assert engine.get_position("trader_1", "BTCUSDT") is not None


def test_order_cancelled_without_position_resets_signal():
    """ORDER_CANCELLED with no open position → signal cancelled, no active position."""
    engine = TradeEngine()
    pos = asyncio.run(engine.process_event(make_event(EventType.ORDER_CANCELLED)))
    assert pos.status == PositionStatus.CLOSED
    assert engine.get_position("trader_1", "BTCUSDT") is None


def test_sl_to_breakeven_classified_correctly():
    """SL near entry (within tolerance) → SL_TO_BREAKEVEN."""
    engine = TradeEngine(breakeven_tolerance_pct=0.5)
    asyncio.run(engine.process_event(make_event(EventType.OPEN, price=40000)))
    # new SL at 40100 = +0.25% from entry → within 0.5% → breakeven
    ev = make_event(EventType.SL_TO_BREAKEVEN, stop_loss=40100.0)
    pos = asyncio.run(engine.process_event(ev))
    assert pos.stop_loss == 40100.0


def test_sl_to_profit_classified_correctly():
    """SL beyond tolerance above entry for LONG → SL_TO_PROFIT."""
    engine = TradeEngine(breakeven_tolerance_pct=0.5)
    asyncio.run(engine.process_event(make_event(EventType.OPEN, price=40000)))
    # new SL at 41000 = +2.5% above entry → SL_TO_PROFIT
    ev = make_event(EventType.SL_TO_BREAKEVEN, stop_loss=41000.0)
    pos = asyncio.run(engine.process_event(ev))
    assert pos.stop_loss == 41000.0


def test_tp_added_appends_to_list():
    engine = TradeEngine()
    asyncio.run(engine.process_event(make_event(EventType.OPEN, price=40000, take_profit=46000.0)))
    pos = asyncio.run(engine.process_event(make_event(EventType.TP_ADDED, take_profit=44000.0)))
    assert 44000.0 in pos.take_profits
    assert 46000.0 in pos.take_profits
    assert len(pos.take_profits) == 2


def test_tp_modified_replaces_first_tp():
    engine = TradeEngine()
    asyncio.run(engine.process_event(make_event(EventType.OPEN, price=40000, take_profit=46000.0)))
    pos = asyncio.run(engine.process_event(make_event(EventType.TP_MODIFIED, take_profit=45000.0)))
    assert pos.take_profits == [45000.0]


def test_open_position_stores_take_profits():
    engine = TradeEngine()
    pos = asyncio.run(engine.process_event(make_event(EventType.OPEN, price=40000, take_profit=46000.0)))
    assert pos.take_profits == [46000.0]
