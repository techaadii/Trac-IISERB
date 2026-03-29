"""
session.py
==========
Database connection setup.
Creates async engine + session factory.
All routes get a session via the get_db() dependency.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import settings

# asyncpg driver for async PostgreSQL
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,          # set True to log all SQL queries (useful for debugging)
    pool_size=10,        # max persistent connections
    max_overflow=20,     # extra connections allowed under heavy load
)

AsyncSessionLocal = sessionmaker(
    bind        = engine,
    class_      = AsyncSession,
    expire_on_commit = False,
)

async def get_db():
    """
    FastAPI dependency — injects a database session into any route.
    Automatically closes the session when the request is done.

    Usage in a route:
        async def my_route(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise