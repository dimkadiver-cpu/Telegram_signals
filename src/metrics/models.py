from dataclasses import dataclass


@dataclass
class MetricsResult:
    """Computed risk/reward metrics for a position."""
    risk_pct: float | None = None         # % of capital at risk
    risk_usd: float | None = None         # USD at risk
    rr: float | None = None               # Risk/Reward ratio (vs first TP)
    delta_exposure: float | None = None   # size × current_price
    effective_leverage: float | None = None
    # Multi-TP / trade-close fields
    tp_index: int | None = None           # 1-based index of the TP just hit
    is_final_close: bool = False          # True when position fully closed
    total_pnl_usd: float | None = None    # Cumulative PnL for the whole trade
    total_pnl_pct: float | None = None    # total_pnl_usd as % of capital
    trade_duration_hours: float | None = None  # Hours from open to close
