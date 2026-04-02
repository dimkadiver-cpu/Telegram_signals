from src.templates.renderer import TemplateRenderer
from src.trade_engine.position import Position, PositionStatus
from src.metrics.models import MetricsResult
from src.events.types import EventType, Side


def make_position() -> Position:
    return Position(
        trader_id="t1",
        symbol="BTCUSDT",
        side=Side.LONG,
        size=0.1,
        avg_entry=40000.0,
        stop_loss=38000.0,
        take_profit=46000.0,
    )


def test_render_open():
    renderer = TemplateRenderer()
    pos = make_position()
    metrics = MetricsResult(risk_pct=5.0, risk_usd=500.0, rr=3.0,
                            delta_exposure=4000.0, effective_leverage=0.4)
    text = renderer.render(EventType.OPEN, pos, metrics)
    assert "OPEN" in text
    assert "BTCUSDT" in text
    assert "40000" in text


def test_render_close():
    renderer = TemplateRenderer()
    pos = make_position()
    pos.realized_pnl = 600.0
    text = renderer.render(EventType.CLOSE, pos)
    assert "CLOSE" in text
    assert "600" in text


def test_render_custom_template():
    custom = "Signal: {{ side }} {{ symbol }} @ {{ entry_price }}"
    renderer = TemplateRenderer(custom_template=custom)
    pos = make_position()
    text = renderer.render(EventType.OPEN, pos)
    assert text == "Signal: LONG BTCUSDT @ 40000.0"
