# import asyncio
from datetime import date
from decimal import Decimal

# from typing import AsyncGenerator
# from fastapi_cache import FastAPICache
# from fastapi_cache.backends.redis import RedisBackend
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import settings
from src.core.db_depends import get_async_session
from src.main import app as prod_app

# from src.core.redis_utils import redis_fabcric
from src.models.base import Base
from src.models.trading_results import SpamixTradingResults


@pytest_asyncio.fixture(scope='function')
async def test_engine():
    engine = create_async_engine(
        settings.database_url,
        echo=True,
        future=True,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope='function')
async def db_session(test_engine):
    return sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope='function')
async def app_test(db_session):
    async def _get_db():
        async with db_session() as session:
            yield session
            await session.rollback()

    prod_app.dependency_overrides[get_async_session] = _get_db
    yield prod_app
    prod_app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(app_test: FastAPI):
    transport = ASGITransport(app=app_test)
    async with AsyncClient(transport=transport, base_url='http://testserver') as client:
        yield client


@pytest_asyncio.fixture
async def trading_results(db_session):
    rows = [
        SpamixTradingResults(
            exchange_product_id='DT32KOB065F',
            exchange_product_name='ДТ (ДТ-З-К5) минус 32, ст. Комбинатская (ст. отправления)',
            oil_id='DT32',
            delivery_basis_id='KOB',
            delivery_basis_name='ст. Комбинатская',
            delivery_type_id='F',
            volume=3120,
            total=Decimal('142696450.00'),
            count=13,
            date=date(2023, 2, 1),
        ),
        SpamixTradingResults(
            exchange_product_id='A106PDK060J',
            exchange_product_name=(
                'Бензин (АИ-100-К5) EURO-6, Предкомбинатская-группа станций (ст. отправления ОТП)'
            ),
            oil_id='A106',
            delivery_basis_id='PDK',
            delivery_basis_name='Предкомбинатская-группа станций',
            delivery_type_id='J',
            volume=60,
            total=Decimal('5514420.00'),
            count=1,
            date=date(2025, 11, 28),
        ),
    ]
    async with db_session() as test_session:
        test_session.add_all(rows)
        await test_session.commit()
        return rows
