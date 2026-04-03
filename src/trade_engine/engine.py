import logging
from datetime import datetime
from typing import TYPE_CHECKING
from src.events.models import TradeEvent
from src.events.types import EventType, Side
from .position import Position, PositionStatus

if TYPE_CHECKING:
    from src.db.position_repository import PositionRepository

logger = logging.getLogger(__name__)

_DEFAULT_BREAKEVEN_TOLERANCE_PCT = 0.5


class TradeEngine:
    """Maintains position state by applying normalized trade events."""

    def __init__(
        self,
        position_repo: "PositionRepository | None" = None,
        breakeven_tolerance_pct: float = _DEFAULT_BREAKEVEN_TOLERANCE_PCT,
    ) -> None:
        # In-memory store keyed by (trader_id, symbol); persisted via DB layer separately
        self._positions: dict[tuple[str, str], Position] = {}
        self._repo = position_repo
        self._breakeven_tolerance_pct = breakeven_tolerance_pct

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
            case EventType.TP_HIT:
                position = self._tp_hit(key, event)
            case EventType.CLOSE | EventType.SL_HIT | EventType.LIQUIDATION:
                position = self._close(key, event)
            case EventType.ORDER_CANCELLED:
                position = self._order_cancelled(key, event)
                if position.status == PositionStatus.CLOSED and key not in self._positions:
                    # Signal cancelled with no prior position: don't persist phantom state
                    if self._repo is not None:
                        await self._repo.save(position)
                    return position
            case EventType.SL_TO_BREAKEVEN | EventType.SL_TO_PROFIT:
                event = self._classify_sl_event(key, event)
                position = self._update_sl(key, event)
            case EventType.TP_MODIFIED:
                position = self._tp_modified(key, event)
            case EventType.TP_ADDED:
                position = self._tp_added(key, event)
            case _:
                logger.warning("Unhandled event type: %s", event.event_type)
                position = self._positions.get(key, self._open(key, event))

        self._positions[key] = position
        if self._repo is not None:
            await self._repo.save(position)
        return position

    def get_position(self, trader_id: str, symbol: str) -> Position | None:
        return self._positions.get((trader_id, symbol))

    # ── private helpers ──────────────────────────────────────────────────────

    def _open(self, key: tuple, event: TradeEvent) -> Position:
        return Position(
            trader_id=event.trader_id,
            symbol=event.symbol,
            side=event.side,
            size=event.size,
            avg_entry=event.price,
            stop_loss=event.stop_loss,
            take_profits=[event.take_profit] if event.take_profit else [],
            initial_size=event.size,
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

    def _tp_hit(self, key: tuple, event: TradeEvent) -> Position:
        """Handle a TP fill: partial close or final close depending on remaining size."""
        pos = self._positions.get(key) or self._open(key, event)
        fill_size = min(event.size, pos.size)

        # Compute PnL for this fill only
        if pos.side == Side.LONG:
            partial_pnl = (event.price - pos.avg_entry) * fill_size
        else:
            partial_pnl = (pos.avg_entry - event.price) * fill_size

        pos.cumulative_realized_pnl += partial_pnl
        pos.size = max(0.0, pos.size - fill_size)
        pos.tp_hit_count += 1

        # Remove the TP level just hit (first remaining level)
        if pos.take_profits:
            pos.take_profits.pop(0)

        if pos.size < 1e-8:
            # Final TP — close position
            pos.size = 0.0
            pos.realized_pnl = pos.cumulative_realized_pnl
            pos.status = PositionStatus.CLOSED
            pos.closed_at = datetime.utcnow()
            self._positions.pop(key, None)
            logger.info(
                "TP_HIT final #%d for %s/%s — full close, total PnL=%.2f",
                pos.tp_hit_count, event.trader_id, event.symbol, pos.realized_pnl,
            )
        else:
            # Intermediate TP — position remains open with reduced size
            self._positions[key] = pos
            logger.info(
                "TP_HIT intermediate #%d for %s/%s — remaining size=%.4f, cumPnL=%.2f",
                pos.tp_hit_count, event.trader_id, event.symbol, pos.size, pos.cumulative_realized_pnl,
            )
        return pos

    def _close(self, key: tuple, event: TradeEvent) -> Position:
        pos = self._positions.pop(key, None) or self._open(key, event)
        if pos.side == Side.LONG:
            close_pnl = (event.price - pos.avg_entry) * pos.size
        else:
            close_pnl = (pos.avg_entry - event.price) * pos.size
        pos.realized_pnl = pos.cumulative_realized_pnl + close_pnl
        pos.cumulative_realized_pnl = pos.realized_pnl
        pos.status = PositionStatus.CLOSED
        pos.closed_at = datetime.utcnow()
        return pos

    def _order_cancelled(self, key: tuple, event: TradeEvent) -> Position:
        """Handle cancellation of a pending order.

        - Position open → DCA order cancelled; position stays open, DCA plan abandoned.
        - No position → signal cancelled entirely; remove any phantom state and reset.
        """
        if key in self._positions:
            # DCA order cancelled: position remains, log and return current state
            pos = self._positions[key]
            logger.info(
                "DCA order cancelled for %s/%s (order_id=%s, type=%s).",
                event.trader_id, event.symbol, event.order_id, event.order_type,
            )
            return pos
        else:
            # Signal cancelled before entry: return a synthetic closed position
            logger.info(
                "Signal cancelled (no open position) for %s/%s.",
                event.trader_id, event.symbol,
            )
            pos = self._open(key, event)
            pos.status = PositionStatus.CLOSED
            pos.closed_at = datetime.utcnow()
            # Remove from map so next entry is treated as a fresh signal
            self._positions.pop(key, None)
            return pos

    def _classify_sl_event(self, key: tuple, event: TradeEvent) -> TradeEvent:
        """Reclassify SL_TO_BREAKEVEN to SL_TO_PROFIT when new SL is in profit territory."""
        pos = self._positions.get(key)
        if pos is None or event.stop_loss is None:
            return event
        new_sl = event.stop_loss
        entry = pos.avg_entry
        tolerance = entry * (self._breakeven_tolerance_pct / 100)
        if pos.side == Side.LONG:
            in_profit = new_sl > entry + tolerance
        else:
            in_profit = new_sl < entry - tolerance
        from dataclasses import replace as dc_replace
        return dc_replace(
            event,
            event_type=EventType.SL_TO_PROFIT if in_profit else EventType.SL_TO_BREAKEVEN,
        )

    def _update_sl(self, key: tuple, event: TradeEvent) -> Position:
        """Move stop loss to the new value carried by the event."""
        pos = self._positions.get(key)
        if pos is None:
            logger.warning("SL move received but no open position for %s/%s.", event.trader_id, event.symbol)
            pos = self._open(key, event)
        pos.stop_loss = event.stop_loss
        logger.info(
            "%s for %s/%s → new SL: %s",
            event.event_type, event.trader_id, event.symbol, event.stop_loss,
        )
        return pos

    def _tp_modified(self, key: tuple, event: TradeEvent) -> Position:
        """Replace the closest TP level with the new value from the event."""
        pos = self._positions.get(key)
        if pos is None:
            logger.warning("TP_MODIFIED received but no open position for %s/%s.", event.trader_id, event.symbol)
            pos = self._open(key, event)
        if event.take_profit is not None:
            if pos.take_profits:
                # Replace the nearest TP (first in list, assumed sorted asc for LONG)
                pos.take_profits[0] = event.take_profit
            else:
                pos.take_profits.append(event.take_profit)
            logger.info("TP_MODIFIED for %s/%s → new TP: %s", event.trader_id, event.symbol, event.take_profit)
        return pos

    def _tp_added(self, key: tuple, event: TradeEvent) -> Position:
        """Add a new TP level to the position's list."""
        pos = self._positions.get(key)
        if pos is None:
            logger.warning("TP_ADDED received but no open position for %s/%s.", event.trader_id, event.symbol)
            pos = self._open(key, event)
        if event.take_profit is not None and event.take_profit not in pos.take_profits:
            pos.take_profits.append(event.take_profit)
            pos.take_profits.sort(reverse=(pos.side == Side.SHORT))
            logger.info("TP_ADDED for %s/%s → TP list: %s", event.trader_id, event.symbol, pos.take_profits)
        return pos
