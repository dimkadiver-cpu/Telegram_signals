from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Binance
    binance_api_key: str = ""
    binance_api_secret: str = ""
    binance_testnet: bool = False

    # Bybit
    bybit_api_key: str = ""
    bybit_api_secret: str = ""
    bybit_testnet: bool = False

    # Telegram
    telegram_bot_token: str = ""
    telegram_review_chat_id: str = ""
    telegram_channel_id: str = ""

    # Database
    database_url: str = "sqlite+aiosqlite:///./telegram_signals.db"

    # Risk
    risk_capital_usd: float = 10_000.0
    risk_pct: float = 1.0

    # SL movement detection
    breakeven_tolerance_pct: float = 0.5  # % tolerance around entry to classify SL as breakeven
