from dataclasses import dataclass


@dataclass
class MetricsResult:
    """Computed risk/reward metrics for a position."""
    risk_pct: float | None = None         # % of capital at risk
    risk_usd: float | None = None         # USD at risk
    rr: float | None = None               # Risk/Reward ratio
    delta_exposure: float | None = None   # size × current_price
    effective_leverage: float | None = None
