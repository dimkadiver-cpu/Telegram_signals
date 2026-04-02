from src.trade_engine.position import Position
from .config import RiskConfig
from .models import MetricsResult


class MetricCalculator:
    """Computes risk and reward metrics for an open position."""

    def calculate(self, position: Position, config: RiskConfig,
                  current_price: float) -> MetricsResult:
        delta_exposure = position.size * current_price
        effective_leverage = delta_exposure / config.capital_usd if config.capital_usd else None

        risk_pct: float | None = None
        risk_usd: float | None = None
        rr: float | None = None

        if position.stop_loss:
            sl_distance = abs(position.avg_entry - position.stop_loss)
            risk_pct = (sl_distance / position.avg_entry) * 100
            risk_usd = (risk_pct / 100) * config.capital_usd

            if position.take_profit:
                tp_distance = abs(position.take_profit - position.avg_entry)
                rr = tp_distance / sl_distance if sl_distance else None

        return MetricsResult(
            risk_pct=round(risk_pct, 2) if risk_pct is not None else None,
            risk_usd=round(risk_usd, 2) if risk_usd is not None else None,
            rr=round(rr, 2) if rr is not None else None,
            delta_exposure=round(delta_exposure, 2),
            effective_leverage=round(effective_leverage, 2) if effective_leverage else None,
        )
