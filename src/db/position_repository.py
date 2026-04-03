import json
import logging
from sqlmodel import select
from src.db.models import Position as DbPosition, TradeStatus
from src.db.session import get_session
from src.trade_engine.position import Position, PositionStatus
from src.events.types import Side

logger = logging.getLogger(__name__)


class PositionRepository:
    """Persists and restores trading positions from the database."""

    async def save(self, pos: Position) -> None:
        """Upsert an open position; close it when status is CLOSED."""
        async for session in get_session():
            stmt = select(DbPosition).where(
                DbPosition.trader_id == int(pos.trader_id),
                DbPosition.symbol == pos.symbol,
                DbPosition.status == TradeStatus.OPEN,
            )
            result = await session.execute(stmt)
            db_pos = result.scalars().first()

            if pos.status == PositionStatus.CLOSED:
                if db_pos:
                    db_pos.status = TradeStatus.CLOSED
                    await session.commit()
                return

            tps_json = json.dumps(pos.take_profits)
            first_tp = pos.take_profits[0] if pos.take_profits else None
            if db_pos is None:
                db_pos = DbPosition(
                    trader_id=int(pos.trader_id),
                    symbol=pos.symbol,
                    side=pos.side.value,
                    size=pos.size,
                    avg_entry=pos.avg_entry,
                    stop_loss=pos.stop_loss,
                    take_profit=first_tp,
                    take_profits_json=tps_json,
                    initial_size=pos.initial_size or pos.size,
                    tp_hit_count=pos.tp_hit_count,
                    cumulative_realized_pnl=pos.cumulative_realized_pnl,
                    status=TradeStatus.OPEN,
                )
                session.add(db_pos)
            else:
                db_pos.size = pos.size
                db_pos.avg_entry = pos.avg_entry
                db_pos.stop_loss = pos.stop_loss
                db_pos.take_profit = first_tp
                db_pos.take_profits_json = tps_json
                db_pos.tp_hit_count = pos.tp_hit_count
                db_pos.cumulative_realized_pnl = pos.cumulative_realized_pnl

            await session.commit()

    async def load_open_positions(self) -> list[Position]:
        """Load all open positions from DB and return as engine Position objects."""
        positions: list[Position] = []
        async for session in get_session():
            stmt = select(DbPosition).where(DbPosition.status == TradeStatus.OPEN)
            result = await session.execute(stmt)
            rows = result.scalars().all()
            for row in rows:
                try:
                    tps = json.loads(row.take_profits_json or "[]")
                except (json.JSONDecodeError, TypeError):
                    tps = [row.take_profit] if row.take_profit else []
                pos = Position(
                    trader_id=str(row.trader_id),
                    symbol=row.symbol,
                    side=Side(row.side),
                    size=row.size,
                    avg_entry=row.avg_entry,
                    stop_loss=row.stop_loss,
                    take_profits=tps,
                    initial_size=row.initial_size or row.size,
                    tp_hit_count=row.tp_hit_count,
                    cumulative_realized_pnl=row.cumulative_realized_pnl,
                )
                positions.append(pos)
        return positions
