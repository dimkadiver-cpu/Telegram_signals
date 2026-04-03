import logging
from datetime import datetime, timezone
from .models import TradeEvent
from .types import EventType, Side

logger = logging.getLogger(__name__)

# Binance order status values
_FILLED_STATUSES = {"FILLED", "PARTIALLY_FILLED"}
_STOP_ORDER_TYPES = {"STOP", "STOP_MARKET"}
_TP_ORDER_TYPES = {"TAKE_PROFIT", "TAKE_PROFIT_MARKET"}

# CCXT unified order type constants
_CCXT_STOP_TYPES = {"stop", "stop_market", "stop_limit"}
_CCXT_TP_TYPES = {"take_profit", "take_profit_market", "take_profit_limit"}

# Default tolerance used when no engine instance is available at normalize time.
# The engine applies the real classification; here we tag as SL_MOVED generically.
_BREAKEVEN_TOLERANCE_PCT_DEFAULT = 0.5


class EventNormalizer:
    """Converts raw exchange payloads into standardized TradeEvent objects."""

    def __init__(self, breakeven_tolerance_pct: float = _BREAKEVEN_TOLERANCE_PCT_DEFAULT) -> None:
        self._breakeven_tolerance_pct = breakeven_tolerance_pct

    def normalize(self, raw: dict, source: str = "binance") -> TradeEvent | None:
        if source == "binance":
            return self._normalize_binance(raw)
        if source in ("bybit", "ccxt"):
            return self._normalize_ccxt_order(raw)
        logger.warning("Unknown source: %s", source)
        return None

    def _normalize_binance(self, raw: dict) -> TradeEvent | None:
        if raw.get("e") != "ORDER_TRADE_UPDATE":
            return None

        order = raw.get("o", {})
        status = order.get("X")
        order_type = order.get("ot", "")

        trader_id = raw.get("trader_id", "unknown")
        symbol = order.get("s", "")
        side = Side.LONG if order["S"] == "BUY" else Side.SHORT
        timestamp = datetime.fromtimestamp(raw.get("T", 0) / 1000, tz=timezone.utc)
        order_id = order.get("i")

        # ── CANCELED orders ──────────────────────────────────────────────────
        if status == "CANCELED":
            return TradeEvent(
                event_type=EventType.ORDER_CANCELLED,
                symbol=symbol,
                side=side,
                size=float(order.get("q", 0)),   # original quantity
                price=float(order.get("p", 0)),  # order price (may be 0 for market)
                timestamp=timestamp,
                trader_id=trader_id,
                raw_data=raw,
                order_id=order_id,
                order_type=order_type,
            )

        # ── NEW stop/TP orders → SL or TP management ─────────────────────────
        if status == "NEW":
            stop_price = float(order.get("sp", 0))

            if order_type in _STOP_ORDER_TYPES and stop_price:
                # Classify SL movement: needs entry price to compute direction.
                # We embed stop_price in stop_loss and let the engine reclassify
                # to SL_TO_BREAKEVEN / SL_TO_PROFIT based on position entry.
                # We emit a preliminary SL event; engine overwrites event_type.
                return TradeEvent(
                    event_type=EventType.SL_TO_BREAKEVEN,  # engine will reclassify
                    symbol=symbol,
                    side=side,
                    size=float(order.get("q", 0)),
                    price=stop_price,
                    timestamp=timestamp,
                    trader_id=trader_id,
                    raw_data=raw,
                    order_id=order_id,
                    order_type=order_type,
                    stop_loss=stop_price,
                )

            if order_type in _TP_ORDER_TYPES and stop_price:
                return TradeEvent(
                    event_type=EventType.TP_ADDED,
                    symbol=symbol,
                    side=side,
                    size=float(order.get("q", 0)),
                    price=stop_price,
                    timestamp=timestamp,
                    trader_id=trader_id,
                    raw_data=raw,
                    order_id=order_id,
                    order_type=order_type,
                    take_profit=stop_price,
                )

            # Other NEW orders (entry orders) are ignored until filled
            return None

        # ── FILLED orders → existing OPEN/CLOSE logic ─────────────────────────
        if status not in _FILLED_STATUSES:
            return None

        size = float(order.get("l", 0))    # last filled qty
        price = float(order.get("L", 0))   # last filled price
        reduce_only = order.get("R", False)
        event_type = EventType.CLOSE if reduce_only else EventType.OPEN

        return TradeEvent(
            event_type=event_type,
            symbol=symbol,
            side=side,
            size=size,
            price=price,
            timestamp=timestamp,
            trader_id=trader_id,
            raw_data=raw,
            order_id=order_id,
            order_type=order_type,
        )

    def _normalize_ccxt_order(self, raw: dict) -> TradeEvent | None:
        """Normalize a CCXT unified order dict (e.g. from watch_orders) into a TradeEvent."""
        status = raw.get("status", "")
        order_type = (raw.get("type") or "").lower()
        trader_id = raw.get("trader_id", "unknown")
        symbol = raw.get("symbol", "")
        side_raw = raw.get("side", "")
        side = Side.LONG if side_raw == "buy" else Side.SHORT
        reduce_only = raw.get("reduceOnly", False)
        order_id = str(raw.get("id", "")) or None

        # Timestamp: CCXT provides milliseconds in "timestamp"
        ts_ms = raw.get("timestamp")
        if ts_ms:
            timestamp = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
        else:
            timestamp = datetime.now(tz=timezone.utc)

        trigger_price = raw.get("triggerPrice") or raw.get("stopPrice") or 0.0
        trigger_price = float(trigger_price) if trigger_price else 0.0

        # ── CANCELED ─────────────────────────────────────────────────────────
        if status == "canceled":
            return TradeEvent(
                event_type=EventType.ORDER_CANCELLED,
                symbol=symbol,
                side=side,
                size=float(raw.get("amount") or 0),
                price=float(raw.get("price") or 0),
                timestamp=timestamp,
                trader_id=trader_id,
                raw_data=raw,
                order_id=order_id,
                order_type=order_type,
            )

        # ── OPEN stop/TP orders → SL or TP management ────────────────────────
        if status == "open":
            if order_type in _CCXT_STOP_TYPES and trigger_price:
                return TradeEvent(
                    event_type=EventType.SL_TO_BREAKEVEN,  # engine will reclassify
                    symbol=symbol,
                    side=side,
                    size=float(raw.get("amount") or 0),
                    price=trigger_price,
                    timestamp=timestamp,
                    trader_id=trader_id,
                    raw_data=raw,
                    order_id=order_id,
                    order_type=order_type,
                    stop_loss=trigger_price,
                )

            if order_type in _CCXT_TP_TYPES and trigger_price:
                return TradeEvent(
                    event_type=EventType.TP_ADDED,
                    symbol=symbol,
                    side=side,
                    size=float(raw.get("amount") or 0),
                    price=trigger_price,
                    timestamp=timestamp,
                    trader_id=trader_id,
                    raw_data=raw,
                    order_id=order_id,
                    order_type=order_type,
                    take_profit=trigger_price,
                )

            return None

        # ── CLOSED (filled) orders → OPEN or CLOSE ───────────────────────────
        if status == "closed":
            size = float(raw.get("filled") or 0)
            price = float(raw.get("average") or raw.get("price") or 0)
            event_type = EventType.CLOSE if reduce_only else EventType.OPEN
            return TradeEvent(
                event_type=event_type,
                symbol=symbol,
                side=side,
                size=size,
                price=price,
                timestamp=timestamp,
                trader_id=trader_id,
                raw_data=raw,
                order_id=order_id,
                order_type=order_type,
            )

        return None
