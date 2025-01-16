from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine

from ._abstract.tables.base import SQLABase
from ._engine import create_async_engine
from ._session import SessionScope

from .  import users


async def init_tables(engine: AsyncEngine, metadata: MetaData) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)


async def init_db(
    host: str = "127.0.0.1",
    port: int = 5432,
    user: str = "postgres",
    password: str = "postgres",
    database: str = "postgres"
) -> None:
    url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"
    async_engine = create_async_engine(url)
    SessionScope.init_sessionmaker(async_sessionmaker(async_engine, expire_on_commit=False))

    await init_tables(async_engine, SQLABase.metadata)
