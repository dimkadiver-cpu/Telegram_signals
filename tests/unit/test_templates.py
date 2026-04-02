from src.templates.renderer import TemplateRenderer
from src.trade_engine.position import Position
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


def test_render_open_hides_risk_without_sl():
    renderer = TemplateRenderer()
    pos = make_position()
    pos.stop_loss = None
    pos.take_profit = None
    metrics = MetricsResult(
        risk_pct=None, risk_usd=None, rr=None, delta_exposure=4000.0, effective_leverage=0.4
    )
    text = renderer.render(EventType.OPEN, pos, metrics)
    assert "Risk:" not in text
    assert "RR:" not in text
    assert "Leva:" in text


def test_render_add_hides_leverage_when_missing():
    renderer = TemplateRenderer()
    pos = make_position()
    metrics = MetricsResult(
        risk_pct=None, risk_usd=None, rr=None, delta_exposure=4000.0, effective_leverage=None
    )
    text = renderer.render(EventType.ADD, pos, metrics)
    assert "ADD" in text
    assert "Exposure:" in text
    assert "Leva:" not in text


def test_render_sl_hit_uses_realized_pnl():
    renderer = TemplateRenderer()
    pos = make_position()
    pos.realized_pnl = -250.0
    text = renderer.render(EventType.SL_HIT, pos)
    assert "STOP LOSS HIT" in text
    assert "-250" in text


def test_render_tp_hit_uses_realized_pnl():
    renderer = TemplateRenderer()
    pos = make_position()
    pos.realized_pnl = 500.0
    text = renderer.render(EventType.TP_HIT, pos)
    assert "TAKE PROFIT HIT" in text
    assert "500" in text
