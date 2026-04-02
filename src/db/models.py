from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import Field, SQLModel


class TradeStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class DraftStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SENT = "SENT"


class Trader(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    binance_api_key: str
    binance_api_secret: str
    telegram_review_chat_id: str
    telegram_channel_id: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Trade(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    trader_id: int = Field(foreign_key="trader.id")
    symbol: str
    side: str
    size: float
    entry_price: float
    exit_price: Optional[float] = None
    realized_pnl: Optional[float] = None
    status: TradeStatus = TradeStatus.OPEN
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Position(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    trader_id: int = Field(foreign_key="trader.id")
    symbol: str
    side: str
    size: float
    avg_entry: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    status: TradeStatus = TradeStatus.OPEN
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TelegramDraft(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    trader_id: int = Field(foreign_key="trader.id")
    trade_id: Optional[int] = Field(default=None, foreign_key="trade.id")
    chat_id: str
    message_text: str
    telegram_message_id: Optional[int] = None
    status: DraftStatus = DraftStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TraderConfig(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    trader_id: int = Field(foreign_key="trader.id", unique=True)
    capital_usd: float = 10_000.0
    risk_pct: float = 1.0
    max_leverage: float = 10.0


class TraderTemplate(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    trader_id: int = Field(foreign_key="trader.id")
    event_type: str                  # matches EventType enum value
    template_text: str
