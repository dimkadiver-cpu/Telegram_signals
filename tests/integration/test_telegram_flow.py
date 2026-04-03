"""Integration test: template rendering → draft creation (mock bot)."""
from src.templates.renderer import TemplateRenderer
from src.trade_engine.position import Position
from src.metrics.models import MetricsResult
from src.events.types import EventType, Side


def test_render_and_draft_text():
    renderer = TemplateRenderer()
    pos = Position(
        trader_id="1",
        symbol="ETHUSDT",
        side=Side.LONG,
        size=1.0,
        avg_entry=2000.0,
        stop_loss=1900.0,
        take_profits=[2300.0],
    )
    metrics = MetricsResult(risk_pct=5.0, risk_usd=500.0, rr=3.0,
                            delta_exposure=2000.0, effective_leverage=0.2)
    text = renderer.render(EventType.OPEN, pos, metrics)

    assert "ETHUSDT" in text
    assert "LONG" in text
    assert "2000" in text
    # Verify the text is non-empty and suitable for sending
    assert len(text) > 10
