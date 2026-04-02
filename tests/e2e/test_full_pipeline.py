"""E2E test: simulated raw WS events through full pipeline (no real exchange/Telegram)."""
import pytest
from unittest.mock import AsyncMock, patch
from src.events.normalizer import EventNormalizer
from src.trade_engine.engine import TradeEngine
from src.metrics.calculator import MetricCalculator
from src.metrics.config import RiskConfig
from src.templates.renderer import TemplateRenderer
from src.events.types import EventType
from src.trade_engine.position import PositionStatus


EVENTS_SEQUENCE = [
    {  # OPEN LONG
        "e": "ORDER_TRADE_UPDATE", "T": 1700000000000, "trader_id": "t1",
        "o": {"s": "BTCUSDT", "S": "BUY", "X": "FILLED",
              "l": "0.1", "L": "40000", "R": False, "ps": "BOTH", "i": "e1"},
    },
    {  # ADD
        "e": "ORDER_TRADE_UPDATE", "T": 1700001000000, "trader_id": "t1",
        "o": {"s": "BTCUSDT", "S": "BUY", "X": "FILLED",
              "l": "0.05", "L": "41000", "R": False, "ps": "BOTH", "i": "e2"},
    },
    {  # CLOSE
        "e": "ORDER_TRADE_UPDATE", "T": 1700002000000, "trader_id": "t1",
        "o": {"s": "BTCUSDT", "S": "SELL", "X": "FILLED",
              "l": "0.15", "L": "45000", "R": True, "ps": "BOTH", "i": "e3"},
    },
]


@pytest.mark.asyncio
async def test_full_pipeline_sequence():
    normalizer = EventNormalizer()
    engine = TradeEngine()
    calculator = MetricCalculator()
    renderer = TemplateRenderer()
    config = RiskConfig(capital_usd=10_000, risk_pct=1.0)

    sent_drafts = []

    for raw in EVENTS_SEQUENCE:
        event = normalizer.normalize(raw)
        if event is None:
            continue
        position = await engine.process_event(event)
        metrics = calculator.calculate(position, config, current_price=event.price)
        text = renderer.render(event.event_type, position, metrics)
        sent_drafts.append({"text": text, "position": position})

    assert len(sent_drafts) == 3
    assert sent_drafts[-1]["position"].status == PositionStatus.CLOSED
    assert sent_drafts[-1]["position"].realized_pnl > 0
    for draft in sent_drafts:
        assert "BTCUSDT" in draft["text"]
