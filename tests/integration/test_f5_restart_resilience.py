"""F5-07 – Test resilienza restart: le posizioni aperte sopravvivono a un restart del motore."""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.events.normalizer import EventNormalizer
from src.trade_engine.engine import TradeEngine
from src.trade_engine.position import Position, PositionStatus
from src.events.types import Side
from src.db.position_repository import PositionRepository


RAW_OPEN = {
    "e": "ORDER_TRADE_UPDATE",
    "T": 1700000000000,
    "trader_id": "42",
    "o": {
        "s": "ETHUSDT", "S": "BUY", "X": "FILLED",
        "l": "1.0", "L": "2000.0", "R": False, "i": "o1",
    },
}

RAW_ADD = {
    "e": "ORDER_TRADE_UPDATE",
    "T": 1700001000000,
    "trader_id": "42",
    "o": {
        "s": "ETHUSDT", "S": "BUY", "X": "FILLED",
        "l": "1.0", "L": "2100.0", "R": False, "i": "o2",
    },
}


@pytest.mark.asyncio
async def test_position_persisted_on_open():
    """Engine saves position to repo when opened."""
    repo = AsyncMock(spec=PositionRepository)
    engine = TradeEngine(position_repo=repo)
    normalizer = EventNormalizer()

    event = normalizer.normalize(RAW_OPEN)
    pos = await engine.process_event(event)

    repo.save.assert_awaited_once()
    saved_pos = repo.save.call_args[0][0]
    assert saved_pos.symbol == "ETHUSDT"
    assert saved_pos.size == 1.0
    assert saved_pos.status == PositionStatus.OPEN


@pytest.mark.asyncio
async def test_position_restored_and_add_after_restart():
    """After restore_positions, a second fill is routed as ADD (not OPEN)."""
    # Simulate first engine run: open position
    repo = AsyncMock(spec=PositionRepository)
    engine1 = TradeEngine(position_repo=repo)
    normalizer = EventNormalizer()

    event_open = normalizer.normalize(RAW_OPEN)
    await engine1.process_event(event_open)

    # Simulate restart: new engine restores persisted positions
    persisted = [
        Position(
            trader_id="42",
            symbol="ETHUSDT",
            side=Side.LONG,
            size=1.0,
            avg_entry=2000.0,
        )
    ]
    repo2 = AsyncMock(spec=PositionRepository)
    engine2 = TradeEngine(position_repo=repo2)
    engine2.restore_positions(persisted)

    # Second fill should be ADD, not OPEN
    event_add = normalizer.normalize(RAW_ADD)
    pos = await engine2.process_event(event_add)

    # avg_entry should be the weighted average of 2000 and 2100
    expected_avg = (2000.0 * 1.0 + 2100.0 * 1.0) / 2.0
    assert pos.size == pytest.approx(2.0)
    assert pos.avg_entry == pytest.approx(expected_avg)
    assert pos.status == PositionStatus.OPEN


@pytest.mark.asyncio
async def test_restore_positions_populates_engine():
    """restore_positions correctly populates the in-memory store."""
    positions = [
        Position(trader_id="1", symbol="BTCUSDT", side=Side.LONG, size=0.5, avg_entry=50000.0),
        Position(trader_id="2", symbol="SOLUSDT", side=Side.SHORT, size=10.0, avg_entry=100.0),
    ]
    engine = TradeEngine()
    engine.restore_positions(positions)

    assert engine.get_position("1", "BTCUSDT") is not None
    assert engine.get_position("2", "SOLUSDT") is not None
    assert engine.get_position("1", "SOLUSDT") is None
