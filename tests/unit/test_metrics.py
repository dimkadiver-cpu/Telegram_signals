import pytest
from src.metrics.calculator import MetricCalculator
from src.metrics.config import RiskConfig
from src.trade_engine.position import Position
from src.events.types import Side


def make_position(sl: float | None = None, tp: float | None = None) -> Position:
    return Position(
        trader_id="t1",
        symbol="BTCUSDT",
        side=Side.LONG,
        size=0.1,
        avg_entry=40000.0,
        stop_loss=sl,
        take_profit=tp,
    )


def test_metrics_with_sl_tp():
    calc = MetricCalculator()
    config = RiskConfig(capital_usd=10_000, risk_pct=1.0)
    pos = make_position(sl=38000, tp=46000)
    result = calc.calculate(pos, config, current_price=40000)
    assert result.risk_pct == pytest.approx(5.0)
    assert result.risk_usd == pytest.approx(500.0)
    assert result.rr == pytest.approx(3.0)
    assert result.delta_exposure == pytest.approx(4000.0)
    assert result.effective_leverage == pytest.approx(0.4)


def test_metrics_no_sl():
    calc = MetricCalculator()
    config = RiskConfig(capital_usd=10_000)
    pos = make_position()
    result = calc.calculate(pos, config, current_price=40000)
    assert result.risk_pct is None
    assert result.risk_usd is None
    assert result.rr is None
    assert result.delta_exposure == pytest.approx(4000.0)


def test_metrics_short_position():
    calc = MetricCalculator()
    config = RiskConfig(capital_usd=10_000)
    pos = Position(
        trader_id="t1", symbol="BTCUSDT", side=Side.SHORT,
        size=0.1, avg_entry=40000.0, stop_loss=42000.0, take_profit=36000.0
    )
    result = calc.calculate(pos, config, current_price=40000)
    assert result.risk_pct == pytest.approx(5.0)
    assert result.rr == pytest.approx(2.0)


def test_metrics_sl_without_tp():
    calc = MetricCalculator()
    config = RiskConfig(capital_usd=10_000)
    pos = make_position(sl=38000, tp=None)
    result = calc.calculate(pos, config, current_price=40000)
    assert result.risk_pct == pytest.approx(5.0)
    assert result.risk_usd == pytest.approx(500.0)
    assert result.rr is None


def test_metrics_ignores_non_adverse_sl_for_long():
    calc = MetricCalculator()
    config = RiskConfig(capital_usd=10_000)
    pos = make_position(sl=42000, tp=46000)
    result = calc.calculate(pos, config, current_price=40000)
    assert result.risk_pct is None
    assert result.risk_usd is None
    assert result.rr is None
