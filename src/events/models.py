from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from .types import EventType, Side


@dataclass
class TradeEvent:
    """Normalized trade event produced by EventNormalizer."""
    event_type: EventType
    symbol: str
    side: Side
    size: float
    price: float
    timestamp: datetime
    trader_id: str
    raw_data: dict[str, Any] = field(default_factory=dict)
    stop_loss: float | None = None
    take_profit: float | None = None
    order_id: str | None = None
    order_type: str | None = None  # e.g. "STOP_MARKET", "TAKE_PROFIT_MARKET"
