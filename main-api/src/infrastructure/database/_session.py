from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession


class SessionScope:
    _sessionmaker: async_sessionmaker[AsyncSession] | None = None

    @staticmethod
    def init_sessionmaker(sessionmaker: async_sessionmaker[AsyncSession]):
        __class__._sessionmaker = sessionmaker

    @classmethod
    @asynccontextmanager
    async def get_session(cls) -> AsyncSession:
        async with cls._sessionmaker() as session:
            try:
                yield session
            except:
                await session.rollback()
                raise
            finally:
                await session.close()
