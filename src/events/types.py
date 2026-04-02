from enum import Enum


class EventType(str, Enum):
    OPEN = "OPEN"
    CLOSE = "CLOSE"
    ADD = "ADD"
    REDUCE = "REDUCE"
    SL_HIT = "SL_HIT"
    TP_HIT = "TP_HIT"
    LIQUIDATION = "LIQUIDATION"


class Side(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"
