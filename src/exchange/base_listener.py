from abc import ABC, abstractmethod
from typing import Callable, Awaitable

RawEventCallback = Callable[[dict], Awaitable[None]]


class BaseListener(ABC):
    """Abstract base class for exchange event listeners."""

    def __init__(self, trader_id: str, on_event: RawEventCallback) -> None:
        self.trader_id = trader_id
        self.on_event = on_event
        self._running = False

    @abstractmethod
    async def start(self) -> None:
        """Start listening for exchange events."""
        ...

    @abstractmethod
    async def stop(self) -> None:
        """Stop listening and clean up resources."""
        ...
