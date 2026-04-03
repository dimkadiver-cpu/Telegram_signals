from src.events.models import TradeEvent
from src.events.types import EventType
from src.trade_engine.position import Position
from src.metrics.models import MetricsResult
from .engine import TemplateEngine

_EVENT_TEMPLATE_MAP: dict[EventType, str] = {
    EventType.OPEN: "open.j2",
    EventType.CLOSE: "close.j2",
    EventType.ADD: "add.j2",
    EventType.REDUCE: "reduce.j2",
    EventType.SL_HIT: "sl_hit.j2",
    EventType.TP_HIT: "tp_hit.j2",
    EventType.LIQUIDATION: "close.j2",
    EventType.ORDER_CANCELLED: "order_cancelled.j2",
    EventType.SL_TO_BREAKEVEN: "sl_to_breakeven.j2",
    EventType.SL_TO_PROFIT: "sl_to_profit.j2",
    EventType.TP_MODIFIED: "tp_modified.j2",
    EventType.TP_ADDED: "tp_added.j2",
}


class TemplateRenderer:
    """Selects and renders the correct template for a trade event."""

    def __init__(self, engine: TemplateEngine | None = None,
                 custom_template: str | None = None) -> None:
        self._engine = engine or TemplateEngine()
        self._custom_template = custom_template

    def render(self, event_type: EventType, position: Position,
               metrics: MetricsResult | None = None,
               custom_template: str | None = None,
               event: TradeEvent | None = None) -> str:
        context = {
            "symbol": position.symbol,
            "side": position.side.value,
            "size": position.size,
            "entry_price": position.avg_entry,
            "stop_loss": position.stop_loss,
            "take_profits": position.take_profits,
            # keep singular for backwards compat with existing templates
            "take_profit": position.take_profits[0] if position.take_profits else None,
            "realized_pnl": position.realized_pnl,
            "metrics": metrics,
            "event": event,
        }
        template_override = custom_template or self._custom_template
        if template_override:
            return self._engine.render_string(template_override, context)
        template_name = _EVENT_TEMPLATE_MAP.get(event_type, "open.j2")
        return self._engine.render_file(template_name, context)
