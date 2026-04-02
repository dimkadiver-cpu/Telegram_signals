from dataclasses import dataclass


@dataclass
class RiskConfig:
    """Per-trader risk configuration."""
    capital_usd: float = 10_000.0
    risk_pct: float = 1.0        # % of capital risked per trade
    max_leverage: float = 10.0
