from typing import Any, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .config import settings

# echo=True отображает запросы SQL, убрать в проде.
engine = create_async_engine(settings.database_url, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, Any]:
    """Асинхронная зависимость FastAPI для получения сессии SQLAlchemy."""
    async with AsyncSessionLocal() as async_session:
        yield async_session
