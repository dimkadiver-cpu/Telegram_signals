from enum import Enum


class EventType(str, Enum):
    OPEN = "OPEN"
    CLOSE = "CLOSE"
    ADD = "ADD"
    REDUCE = "REDUCE"
    SL_HIT = "SL_HIT"
    TP_HIT = "TP_HIT"
    LIQUIDATION = "LIQUIDATION"
    # Cancellation
    ORDER_CANCELLED = "ORDER_CANCELLED"
    # Stop loss movements
    SL_TO_BREAKEVEN = "SL_TO_BREAKEVEN"
    SL_TO_PROFIT = "SL_TO_PROFIT"
    # Take profit changes
    TP_MODIFIED = "TP_MODIFIED"
    TP_ADDED = "TP_ADDED"


class Side(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"
