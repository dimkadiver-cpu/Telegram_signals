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

            if db_pos is None:
                db_pos = DbPosition(
                    trader_id=int(pos.trader_id),
                    symbol=pos.symbol,
                    side=pos.side.value,
                    size=pos.size,
                    avg_entry=pos.avg_entry,
                    stop_loss=pos.stop_loss,
                    take_profit=pos.take_profit,
                    status=TradeStatus.OPEN,
                )
                session.add(db_pos)
            else:
                db_pos.size = pos.size
                db_pos.avg_entry = pos.avg_entry
                db_pos.stop_loss = pos.stop_loss
                db_pos.take_profit = pos.take_profit

            await session.commit()

    async def load_open_positions(self) -> list[Position]:
        """Load all open positions from DB and return as engine Position objects."""
        positions: list[Position] = []
        async for session in get_session():
            stmt = select(DbPosition).where(DbPosition.status == TradeStatus.OPEN)
            result = await session.execute(stmt)
            rows = result.scalars().all()
            for row in rows:
                pos = Position(
                    trader_id=str(row.trader_id),
                    symbol=row.symbol,
                    side=Side(row.side),
                    size=row.size,
                    avg_entry=row.avg_entry,
                    stop_loss=row.stop_loss,
                    take_profit=row.take_profit,
                )
                positions.append(pos)
        return positions
