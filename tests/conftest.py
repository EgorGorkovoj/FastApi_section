import asyncio
import subprocess
import time
from datetime import date
from decimal import Decimal

import asyncpg
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from src.core.config import Config, settings
from src.core.db_depends import get_async_session
from src.core.logger import logger
from src.core.redis_utils import get_redis, redis_cache, redis_manager
from src.main import app as prod_app
from src.models.base import Base
from src.models.trading_results import SpamixTradingResults


@pytest_asyncio.fixture(scope='session', autouse=True)
async def setup_test_db():
    """
    Фикстура для автоматического запуска и удаления контейнера с тестовой базой данных.

    - Перед тестами запускает контейнер PostgreSQL с помощью `docker compose`.
    - Ожидает готовности базы перед выполнением тестов.
    - После тестов останавливает и удаляет контейнер с тестовой БД.
    """
    try:
        subprocess.run(
            [
                'docker',
                'compose',
                '--env-file',
                '.test.env',
                '-f',
                'docker-compose.test.yml',
                'up',
                '-d',
            ],
            check=True,
        )
        await wait_for_postgres_async(settings=settings)
        yield
    finally:
        subprocess.run(
            ['docker', 'compose', '-f', 'docker-compose.test.yml', 'down', '-v'],
            check=True,
        )


async def wait_for_postgres_async(settings: Config, timeout: int = 60):
    """Асинхронно ждём готовности PostgreSQL."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            conn = await asyncpg.connect(
                host=settings.POSTGRES_HOST,
                port=settings.POSTGRES_PORT,
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                database=settings.POSTGRES_DB,
            )
            await conn.close()
            logger.info('PostgreSQL готов к работе')
            return
        except (OSError, asyncpg.PostgresError):
            logger.info('Ожидание PostgreSQL...')
            await asyncio.sleep(1)
    raise TimeoutError('PostgreSQL не запустился за отведённое время!')


@pytest_asyncio.fixture(scope='session')
async def test_engine():
    engine = create_async_engine(
        settings.database_url, echo=False, future=True, poolclass=NullPool
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture(scope='session')
async def async_sessionmaker(test_engine):
    return sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope='session')
async def app_test(async_sessionmaker):
    async def _get_db():
        async with async_sessionmaker() as session:
            try:
                yield session
            finally:
                await session.rollback()

    prod_app.dependency_overrides[get_async_session] = _get_db
    yield prod_app
    prod_app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope='session')
async def check_init_redis():
    redic = await get_redis(redis_manager=redis_manager)
    await redis_cache.init_fastapi_cache()
    yield redic
    await redic.flushdb()


@pytest_asyncio.fixture
async def client(app_test: FastAPI, check_init_redis):
    transport = ASGITransport(app=app_test)
    async with AsyncClient(transport=transport, base_url='http://testserver') as c:
        yield c


@pytest_asyncio.fixture(scope='session')
async def trading_results(async_sessionmaker):
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
    async with async_sessionmaker() as test_session:
        test_session.add_all(rows)
        await test_session.commit()
        return rows
