from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine as create_async_engine_, AsyncEngine


def create_async_engine(url: URL | str) -> AsyncEngine:
    return create_async_engine_(url, future=True)
