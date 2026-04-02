from src.trade_engine.position import Position
from src.events.types import Side
from .config import RiskConfig
from .models import MetricsResult


class MetricCalculator:
    """Computes risk and reward metrics for an open position."""

    def calculate(self, position: Position, config: RiskConfig,
                  current_price: float) -> MetricsResult:
        delta_exposure = position.size * current_price
        effective_leverage = (
            delta_exposure / config.capital_usd if config.capital_usd else None
        )

        risk_pct: float | None = None
        risk_usd: float | None = None
        rr: float | None = None

        if position.stop_loss:
            sl_distance = self._adverse_distance(position, position.stop_loss)
            if sl_distance > 0:
                risk_pct = (sl_distance / position.avg_entry) * 100
                risk_usd = (risk_pct / 100) * config.capital_usd

                if position.take_profit:
                    tp_distance = self._favorable_distance(position, position.take_profit)
                    rr = tp_distance / sl_distance if tp_distance > 0 else None

        return MetricsResult(
            risk_pct=round(risk_pct, 2) if risk_pct is not None else None,
            risk_usd=round(risk_usd, 2) if risk_usd is not None else None,
            rr=round(rr, 2) if rr is not None else None,
            delta_exposure=round(delta_exposure, 2),
            effective_leverage=(
                round(effective_leverage, 2)
                if effective_leverage is not None
                else None
            ),
        )

    @staticmethod
    def _adverse_distance(position: Position, price: float) -> float:
        if position.side == Side.LONG:
            return position.avg_entry - price
        return price - position.avg_entry

    @staticmethod
    def _favorable_distance(position: Position, price: float) -> float:
        if position.side == Side.LONG:
            return price - position.avg_entry
        return position.avg_entry - price
