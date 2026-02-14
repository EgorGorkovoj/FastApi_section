"""
Тестовые фикстуры для API trading-results.

Используется dependency_overrides FastAPI для:
- подмены Redis
- подмены AsyncSession
- изоляции от реальной БД и Redis

Фикстуры:
- app_test — тестовое приложение
- client — httpx AsyncClient с ASGITransport
- fake_redis — мок Redis-клиента
- session_mock — мок AsyncSession
- override_redis — подмена зависимости get_redis
- override_session — подмена зависимости get_async_session
- fake_trade — фабрика фейковых trade-объектов
"""

from datetime import date
from decimal import Decimal
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.api.v1.endpoints.trading import get_async_session, get_redis
from src.main import app as prod_app


@pytest_asyncio.fixture
async def app_test() -> FastAPI:
    return prod_app


@pytest_asyncio.fixture
async def client(app_test: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app_test),
        base_url='http://testserver',
    ) as client:
        yield client


@pytest.fixture
def fake_redis() -> AsyncMock:
    cache = AsyncMock()
    cache.get.return_value = None
    cache.set.return_value = None
    return cache


@pytest.fixture
def session_mock() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def override_redis(app_test: FastAPI, fake_redis: AsyncMock) -> Generator[AsyncMock, None, None]:
    async def _override():
        return fake_redis

    app_test.dependency_overrides[get_redis] = _override
    yield fake_redis
    app_test.dependency_overrides.pop(get_redis, None)


@pytest.fixture
def override_session(
    app_test: FastAPI, session_mock: AsyncMock
) -> Generator[AsyncMock, None, None]:
    async def _override():
        yield session_mock

    app_test.dependency_overrides[get_async_session] = _override
    yield session_mock
    app_test.dependency_overrides.pop(get_async_session, None)


@pytest_asyncio.fixture
async def fake_trade() -> type:
    class FakeTrade:
        def __init__(self, i):
            self.oil_id = f'A{i}'
            self.exchange_product_id = f'EP{i}'
            self.exchange_product_name = f'Product {i}'
            self.delivery_basis_id = f'B{i}'
            self.delivery_basis_name = f'Basis {i}'
            self.delivery_type_id = f'D{i}'
            self.volume = 100 + i
            self.total = Decimal(f'{1000 + i}.50')
            self.count = i
            self.date = date(2024, 1, i + 1)

        def to_dict(self):
            return {
                'oil_id': self.oil_id,
                'exchange_product_id': self.exchange_product_id,
                'exchange_product_name': self.exchange_product_name,
                'delivery_basis_id': self.delivery_basis_id,
                'delivery_basis_name': self.delivery_basis_name,
                'delivery_type_id': self.delivery_type_id,
                'volume': self.volume,
                'total': str(self.total),
                'count': self.count,
                'date': self.date.isoformat(),
            }

    return FakeTrade
