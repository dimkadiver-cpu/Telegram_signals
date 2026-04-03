from src.events.normalizer import EventNormalizer
from src.events.types import EventType, Side


def _binance_order_payload(side="BUY", status="FILLED", reduce_only=False,
                            order_type="LIMIT", stop_price=0.0, close_pos=False) -> dict:
    return {
        "e": "ORDER_TRADE_UPDATE",
        "T": 1700000000000,
        "trader_id": "trader_1",
        "o": {
            "s": "BTCUSDT",
            "S": side,
            "X": status,
            "ot": order_type,
            "l": "0.01",       # last filled qty
            "L": "40000.0",    # last filled price
            "q": "0.1",        # original qty
            "p": "40000.0",    # order price
            "sp": str(stop_price),
            "R": reduce_only,
            "cp": close_pos,
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
    # NEW with non-stop order type → ignored
    raw = _binance_order_payload(status="NEW", order_type="LIMIT")
    assert normalizer.normalize(raw) is None


def test_ignore_wrong_event_type():
    normalizer = EventNormalizer()
    raw = {"e": "ACCOUNT_UPDATE", "trader_id": "t1"}
    assert normalizer.normalize(raw) is None


def test_normalize_canceled_order():
    normalizer = EventNormalizer()
    raw = _binance_order_payload(status="CANCELED", order_type="STOP_MARKET")
    event = normalizer.normalize(raw)
    assert event is not None
    assert event.event_type == EventType.ORDER_CANCELLED
    assert event.order_type == "STOP_MARKET"
    assert event.order_id == "order_123"


def test_normalize_sl_moved_new_stop_market():
    normalizer = EventNormalizer()
    raw = _binance_order_payload(status="NEW", order_type="STOP_MARKET", stop_price=39000.0)
    event = normalizer.normalize(raw)
    assert event is not None
    # emitted as SL_TO_BREAKEVEN (engine reclassifies to SL_TO_PROFIT if needed)
    assert event.event_type == EventType.SL_TO_BREAKEVEN
    assert event.stop_loss == 39000.0


def test_normalize_tp_added_new_tp_market():
    normalizer = EventNormalizer()
    raw = _binance_order_payload(status="NEW", order_type="TAKE_PROFIT_MARKET", stop_price=45000.0)
    event = normalizer.normalize(raw)
    assert event is not None
    assert event.event_type == EventType.TP_ADDED
    assert event.take_profit == 45000.0
