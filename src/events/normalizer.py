import logging
from datetime import datetime, timezone
from .models import TradeEvent
from .types import EventType, Side

logger = logging.getLogger(__name__)

# Binance order status that represents a filled trade
_FILLED_STATUSES = {"FILLED", "PARTIALLY_FILLED"}


class EventNormalizer:
    """Converts raw exchange payloads into standardized TradeEvent objects."""

    def normalize(self, raw: dict, source: str = "binance") -> TradeEvent | None:
        if source == "binance":
            return self._normalize_binance(raw)
        logger.warning("Unknown source: %s", source)
        return None

    def _normalize_binance(self, raw: dict) -> TradeEvent | None:
        # Only process ORDER_TRADE_UPDATE events with filled orders
        if raw.get("e") != "ORDER_TRADE_UPDATE":
            return None
        order = raw.get("o", {})
        if order.get("X") not in _FILLED_STATUSES:
            return None

        trader_id = raw.get("trader_id", "unknown")
        side = Side.LONG if order["S"] == "BUY" else Side.SHORT
        size = float(order.get("l", 0))  # last filled qty
        price = float(order.get("L", 0))  # last filled price
        reduce_only = order.get("R", False)
        timestamp = datetime.fromtimestamp(raw.get("T", 0) / 1000, tz=timezone.utc)

        # Determine event type
        position_side = order.get("ps", "BOTH")
        if reduce_only or position_side == "BOTH" and order.get("S") != order.get("ps"):
            event_type = EventType.CLOSE
        else:
            event_type = EventType.OPEN  # TODO: distinguish ADD/REDUCE from open position

        return TradeEvent(
            event_type=event_type,
            symbol=order.get("s", ""),
            side=side,
            size=size,
            price=price,
            timestamp=timestamp,
            trader_id=trader_id,
            raw_data=raw,
            order_id=order.get("i"),
        )
