from datetime import datetime
from src.trade_engine.position import Position, PositionStatus
from src.events.types import EventType, Side
from .config import RiskConfig
from .models import MetricsResult


class MetricCalculator:
    """Computes risk and reward metrics for an open position."""

    def calculate(
        self,
        position: Position,
        config: RiskConfig,
        current_price: float,
        event_type: EventType | None = None,
    ) -> MetricsResult:
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

                first_tp = position.take_profits[0] if position.take_profits else None
                if first_tp:
                    tp_distance = self._favorable_distance(position, first_tp)
                    rr = tp_distance / sl_distance if tp_distance > 0 else None

        # ── Multi-TP / final-close fields ────────────────────────────────────
        is_final_close = position.status == PositionStatus.CLOSED
        tp_index: int | None = None
        if event_type == EventType.TP_HIT:
            tp_index = position.tp_hit_count  # already incremented by engine

        total_pnl_usd: float | None = None
        total_pnl_pct: float | None = None
        trade_duration_hours: float | None = None

        if is_final_close:
            total_pnl_usd = round(position.cumulative_realized_pnl, 2)
            if config.capital_usd:
                total_pnl_pct = round(
                    (position.cumulative_realized_pnl / config.capital_usd) * 100, 2
                )
            if position.opened_at and position.closed_at:
                delta = position.closed_at - position.opened_at
                trade_duration_hours = round(delta.total_seconds() / 3600, 2)

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
            tp_index=tp_index,
            is_final_close=is_final_close,
            total_pnl_usd=total_pnl_usd,
            total_pnl_pct=total_pnl_pct,
            trade_duration_hours=trade_duration_hours,
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
