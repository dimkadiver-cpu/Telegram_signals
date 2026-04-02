from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage


_bot: Bot | None = None
_dispatcher: Dispatcher | None = None


def get_bot() -> Bot:
    if _bot is None:
        raise RuntimeError("Bot not initialized. Call init_bot() first.")
    return _bot


def get_dispatcher() -> Dispatcher:
    if _dispatcher is None:
        raise RuntimeError("Dispatcher not initialized. Call init_bot() first.")
    return _dispatcher


def init_bot(token: str) -> tuple[Bot, Dispatcher]:
    global _bot, _dispatcher
    _bot = Bot(token=token)
    _dispatcher = Dispatcher(storage=MemoryStorage())
    return _bot, _dispatcher
