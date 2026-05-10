from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# WHY ASYNC ENGINE:
# FastAPI is async. A sync SQLAlchemy engine blocks the event loop during
# every DB query — under load, all requests queue behind each other.
# An async engine releases the event loop during I/O, allowing other requests
# to proceed while one is waiting for the DB response.
# ALTERNATIVE: sync engine with threadpool — works but wastes memory on threads
# and doesn't scale as cleanly.
engine = create_async_engine(
    settings.database_url,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    # pool_pre_ping=True: before handing a connection from the pool to your
    # code, SQLAlchemy checks it is still alive. Prevents "connection closed"
    # errors after the DB restarts or idle connections are dropped.
    echo=not settings.is_production,
    # echo=True logs every SQL query. Useful in dev, too noisy in prod.
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    # expire_on_commit=False: after commit, object attributes remain accessible
    # without re-querying. Without this, accessing obj.id after commit raises
    # a "DetachedInstanceError" in async contexts.
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
