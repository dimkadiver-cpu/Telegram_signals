from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from src.events.types import Side


class PositionStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


@dataclass
class Position:
    """Represents the current state of a trading position."""
    trader_id: str
    symbol: str
    side: Side
    size: float
    avg_entry: float
    status: PositionStatus = PositionStatus.OPEN
    realized_pnl: float = 0.0
    stop_loss: float | None = None
    take_profits: list[float] = field(default_factory=list)
    opened_at: datetime = field(default_factory=datetime.utcnow)
    closed_at: datetime | None = None
    # Multi-TP tracking
    initial_size: float = 0.0
    tp_hit_count: int = 0
    cumulative_realized_pnl: float = 0.0

    def unrealized_pnl(self, current_price: float) -> float:
        if self.side == Side.LONG:
            return (current_price - self.avg_entry) * self.size
        return (self.avg_entry - current_price) * self.size
