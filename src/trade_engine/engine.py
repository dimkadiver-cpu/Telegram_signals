import logging
from datetime import datetime
from typing import TYPE_CHECKING
from src.events.models import TradeEvent
from src.events.types import EventType, Side
from .position import Position, PositionStatus

if TYPE_CHECKING:
    from src.db.position_repository import PositionRepository

logger = logging.getLogger(__name__)


class TradeEngine:
    """Maintains position state by applying normalized trade events."""

    def __init__(self, position_repo: "PositionRepository | None" = None) -> None:
        # In-memory store keyed by (trader_id, symbol); persisted via DB layer separately
        self._positions: dict[tuple[str, str], Position] = {}
        self._repo = position_repo

    def restore_positions(self, positions: list[Position]) -> None:
        """Populate in-memory state from previously persisted positions."""
        for pos in positions:
            key = (pos.trader_id, pos.symbol)
            self._positions[key] = pos
        logger.info("Restored %d open position(s) from DB.", len(positions))

    async def process_event(self, event: TradeEvent) -> Position:
        key = (event.trader_id, event.symbol)

        match event.event_type:
            case EventType.OPEN:
                # If a position already exists for this key, treat fill as ADD
                if key in self._positions:
                    position = self._add(key, event)
                else:
                    position = self._open(key, event)
            case EventType.ADD:
                position = self._add(key, event)
            case EventType.REDUCE:
                position = self._reduce(key, event)
            case EventType.CLOSE | EventType.SL_HIT | EventType.TP_HIT | EventType.LIQUIDATION:
                position = self._close(key, event)
            case _:
                logger.warning("Unhandled event type: %s", event.event_type)
                position = self._positions.get(key, self._open(key, event))

        self._positions[key] = position
        if self._repo is not None:
            await self._repo.save(position)
        return position

    def get_position(self, trader_id: str, symbol: str) -> Position | None:
        return self._positions.get((trader_id, symbol))

    def _open(self, key: tuple, event: TradeEvent) -> Position:
        return Position(
            trader_id=event.trader_id,
            symbol=event.symbol,
            side=event.side,
            size=event.size,
            avg_entry=event.price,
            stop_loss=event.stop_loss,
            take_profit=event.take_profit,
        )

    def _add(self, key: tuple, event: TradeEvent) -> Position:
        pos = self._positions.get(key) or self._open(key, event)
        total_cost = pos.avg_entry * pos.size + event.price * event.size
        pos.size += event.size
        pos.avg_entry = total_cost / pos.size
        return pos

    def _reduce(self, key: tuple, event: TradeEvent) -> Position:
        pos = self._positions.get(key) or self._open(key, event)
        pos.size = max(0.0, pos.size - event.size)
        return pos

    def _close(self, key: tuple, event: TradeEvent) -> Position:
        pos = self._positions.pop(key, None) or self._open(key, event)
        if pos.side == Side.LONG:
            pos.realized_pnl = (event.price - pos.avg_entry) * pos.size
        else:
            pos.realized_pnl = (pos.avg_entry - event.price) * pos.size
        pos.status = PositionStatus.CLOSED
        pos.closed_at = datetime.utcnow()
        return pos
