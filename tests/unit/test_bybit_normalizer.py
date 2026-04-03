"""Unit tests for CCXT-unified order normalization (Bybit path)."""
import pytest
from datetime import timezone
from src.events.normalizer import EventNormalizer
from src.events.types import EventType, Side


@pytest.fixture
def normalizer():
    return EventNormalizer()


def _base_order(**kwargs):
    """Return a minimal CCXT unified order dict."""
    base = {
        "id": "123",
        "symbol": "BTC/USDT:USDT",
        "side": "buy",
        "status": "closed",
        "type": "market",
        "amount": 0.1,
        "filled": 0.1,
        "average": 30000.0,
        "price": 30000.0,
        "reduceOnly": False,
        "triggerPrice": None,
        "stopPrice": None,
        "timestamp": 1_700_000_000_000,
        "trader_id": "42",
        "_source": "bybit",
    }
    base.update(kwargs)
    return base


def test_normalize_ccxt_open_long(normalizer):
    raw = _base_order(status="closed", side="buy", reduceOnly=False, filled=0.5, average=30000.0)
    event = normalizer.normalize(raw, source="bybit")
    assert event is not None
    assert event.event_type == EventType.OPEN
    assert event.side == Side.LONG
    assert event.size == 0.5
    assert event.price == 30000.0
    assert event.trader_id == "42"
    assert event.symbol == "BTC/USDT:USDT"
    assert event.timestamp.tzinfo == timezone.utc


def test_normalize_ccxt_open_short(normalizer):
    raw = _base_order(status="closed", side="sell", reduceOnly=False, filled=0.2, average=29500.0)
    event = normalizer.normalize(raw, source="bybit")
    assert event is not None
    assert event.event_type == EventType.OPEN
    assert event.side == Side.SHORT


def test_normalize_ccxt_close(normalizer):
    raw = _base_order(status="closed", side="sell", reduceOnly=True, filled=0.1, average=31000.0)
    event = normalizer.normalize(raw, source="bybit")
    assert event is not None
    assert event.event_type == EventType.CLOSE
    assert event.side == Side.SHORT
    assert event.price == 31000.0


def test_normalize_ccxt_order_cancelled(normalizer):
    raw = _base_order(status="canceled", side="buy", amount=0.3, price=29000.0)
    event = normalizer.normalize(raw, source="bybit")
    assert event is not None
    assert event.event_type == EventType.ORDER_CANCELLED
    assert event.size == 0.3


def test_normalize_ccxt_sl_moved(normalizer):
    raw = _base_order(
        status="open",
        type="stop",
        side="buy",
        triggerPrice=28500.0,
        amount=0.1,
    )
    event = normalizer.normalize(raw, source="bybit")
    assert event is not None
    assert event.event_type == EventType.SL_TO_BREAKEVEN
    assert event.stop_loss == 28500.0
    assert event.price == 28500.0


def test_normalize_ccxt_sl_moved_stop_market(normalizer):
    raw = _base_order(
        status="open",
        type="stop_market",
        side="sell",
        triggerPrice=32000.0,
        amount=0.05,
    )
    event = normalizer.normalize(raw, source="bybit")
    assert event is not None
    assert event.event_type == EventType.SL_TO_BREAKEVEN
    assert event.stop_loss == 32000.0


def test_normalize_ccxt_tp_added(normalizer):
    raw = _base_order(
        status="open",
        type="take_profit",
        side="buy",
        triggerPrice=35000.0,
        amount=0.1,
    )
    event = normalizer.normalize(raw, source="bybit")
    assert event is not None
    assert event.event_type == EventType.TP_ADDED
    assert event.take_profit == 35000.0
    assert event.price == 35000.0


def test_normalize_ccxt_tp_added_via_ccxt_source(normalizer):
    """Source 'ccxt' also routes to _normalize_ccxt_order."""
    raw = _base_order(
        status="open",
        type="take_profit_market",
        side="sell",
        triggerPrice=28000.0,
        amount=0.2,
    )
    event = normalizer.normalize(raw, source="ccxt")
    assert event is not None
    assert event.event_type == EventType.TP_ADDED


def test_normalize_ccxt_open_status_no_trigger_returns_none(normalizer):
    """An open non-stop/tp order without trigger price should return None."""
    raw = _base_order(status="open", type="limit", triggerPrice=None)
    event = normalizer.normalize(raw, source="bybit")
    assert event is None


def test_normalize_ccxt_unknown_status_returns_none(normalizer):
    raw = _base_order(status="rejected")
    event = normalizer.normalize(raw, source="bybit")
    assert event is None


def test_normalize_ccxt_uses_stopprice_fallback(normalizer):
    """stopPrice should be used when triggerPrice is absent."""
    raw = _base_order(
        status="open",
        type="stop",
        triggerPrice=None,
        stopPrice=27000.0,
        amount=0.1,
    )
    event = normalizer.normalize(raw, source="bybit")
    assert event is not None
    assert event.stop_loss == 27000.0
