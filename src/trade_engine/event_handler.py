from src.events.models import TradeEvent
from .engine import TradeEngine
from .position import Position


class EventHandler:
    """Routes incoming TradeEvents to the TradeEngine."""

    def __init__(self, engine: TradeEngine) -> None:
        self.engine = engine

    async def handle(self, event: TradeEvent) -> Position:
        return await self.engine.process_event(event)
