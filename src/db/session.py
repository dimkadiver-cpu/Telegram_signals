from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

_engine = None
_async_session_factory = None


def init_db(database_url: str) -> None:
    global _engine, _async_session_factory
    _engine = create_async_engine(database_url, echo=False, future=True)
    _async_session_factory = sessionmaker(
        _engine, class_=AsyncSession, expire_on_commit=False
    )


async def create_tables() -> None:
    if _engine is None:
        raise RuntimeError("Database engine not initialized. Call init_db() before create_tables().")
    # Ensure SQLModel metadata is populated before create_all.
    from src.db import models  # noqa: F401

    async with _engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    if _async_session_factory is None:
        raise RuntimeError("Session factory not initialized. Call init_db() before get_session().")
    async with _async_session_factory() as session:
        yield session
