import contextlib
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

from src.conf.config import config

Base = declarative_base()


class DatabaseSessionManager:

    def __init__(self, url: str):
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker | None = async_sessionmaker(autocommit=False, autoflush=False,
                                                                            bind=self._engine)

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._session_maker is None:
            raise Exception("DatabaseSessionManager is not initialized")
        session = self._session_maker()
        try:
            yield session
        except Exception as err:
            print(err)
            await session.rollback()
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(config.DB_URL)


async def get_db() -> AsyncIterator[AsyncSession]:
    """
The get_db function is a context manager that returns an async session.
The session can be used to query the database and add/remove objects from it.


:return: A context manager that returns a session
"""
    async with sessionmanager.session() as session:
        yield session
