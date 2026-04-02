from src.events.normalizer import EventNormalizer
from src.events.types import EventType, Side


def _binance_order_payload(side="BUY", status="FILLED", reduce_only=False) -> dict:
    return {
        "e": "ORDER_TRADE_UPDATE",
        "T": 1700000000000,
        "trader_id": "trader_1",
        "o": {
            "s": "BTCUSDT",
            "S": side,
            "X": status,
            "l": "0.01",       # last filled qty
            "L": "40000.0",    # last filled price
            "R": reduce_only,
            "ps": "BOTH",
            "i": "order_123",
        },
    }


def test_normalize_open_long():
    normalizer = EventNormalizer()
    event = normalizer.normalize(_binance_order_payload(side="BUY"))
    assert event is not None
    assert event.event_type == EventType.OPEN
    assert event.side == Side.LONG
    assert event.size == 0.01
    assert event.price == 40000.0
    assert event.trader_id == "trader_1"


def test_normalize_close_short():
    normalizer = EventNormalizer()
    raw = _binance_order_payload(side="SELL", reduce_only=True)
    event = normalizer.normalize(raw)
    assert event is not None
    assert event.event_type == EventType.CLOSE


def test_ignore_unfilled_order():
    normalizer = EventNormalizer()
    raw = _binance_order_payload(status="NEW")
    assert normalizer.normalize(raw) is None


def test_ignore_wrong_event_type():
    normalizer = EventNormalizer()
    raw = {"e": "ACCOUNT_UPDATE", "trader_id": "t1"}
    assert normalizer.normalize(raw) is None
