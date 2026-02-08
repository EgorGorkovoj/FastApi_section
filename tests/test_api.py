from decimal import Decimal

import pytest
from fastapi import status


@pytest.mark.asyncio(loop_scope='session')
async def test_last_dates_404(client):
    response = await client.get('api/v1/trading-results/last-dates?limit=5&offset=0')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Даты не найдены!'}


@pytest.mark.asyncio(loop_scope='session')
async def test_last_dates_cached(trading_results, client, check_init_redis):
    r1 = await client.get('api/v1/trading-results/last-dates?limit=5&offset=0')
    r2 = await client.get('api/v1/trading-results/last-dates?limit=5&offset=0')

    assert r1.status_code == status.HTTP_200_OK
    assert r2.status_code == status.HTTP_200_OK

    assert r1.json() == r2.json()
    assert len(r1.json()) == 2

    keys = await check_init_redis.keys('fastapi-cache:*')
    assert len(keys) > 0

    value = await check_init_redis.get(keys[0])
    assert value is not None


@pytest.mark.asyncio(loop_scope='session')
async def test_last_dates_pagination(client, trading_results):
    """Проверяем пагинацию"""

    response = await client.get('api/v1/trading-results/last-dates?limit=1&offset=0')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0] == trading_results[1].date.isoformat()

    response = await client.get('api/v1/trading-results/last-dates?limit=1&offset=1')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0] == trading_results[0].date.isoformat()


@pytest.mark.asyncio(loop_scope='session')
async def test_trading_dynamics_404(client):
    """Проверка на 404, если данных нет"""
    params = {
        'limit': 5,
        'offset': 0,
        'oil_id': 'OIL999',
        'start_date': '2024-01-01',
        'end_date': '2024-01-31',
    }

    response = await client.get('api/v1/trading-results/', params=params)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Данные по торгам за заданный период не найдены!'}


@pytest.mark.asyncio(loop_scope='session')
async def test_trading_dynamics_cached(client, trading_results, check_init_redis):
    """Проверяем кэширование и фильтрацию по oil_id"""

    params = {
        'limit': 5,
        'offset': 0,
        'oil_id': 'DT32',
        'start_date': '2023-02-01',
        'end_date': '2025-11-28',
    }

    r1 = await client.get('api/v1/trading-results/', params=params)
    r2 = await client.get('api/v1/trading-results/', params=params)

    assert r1.status_code == status.HTTP_200_OK
    assert r2.status_code == status.HTTP_200_OK

    def normalize_totals(records):
        for r in records:
            r['total'] = Decimal(r['total'])
        return records

    r1_data = normalize_totals(r1.json())
    r2_data = normalize_totals(r2.json())

    assert r1_data == r2_data
    assert len(r1.json()) == 1

    keys = await check_init_redis.keys('fastapi-cache:*')

    assert len(keys) > 0

    value = await check_init_redis.get(keys[0])
    assert value is not None


@pytest.mark.asyncio(loop_scope='session')
async def test_trading_dynamics_pagination(client, trading_results):
    """Проверка limit, offset и фильтров"""

    params = {
        'limit': 1,
        'offset': 0,
        'oil_id': 'DT32',
        'start_date': '2023-02-01',
        'end_date': '2025-11-28',
    }
    response = await client.get('api/v1/trading-results/', params=params)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1

    params['offset'] = 1
    response = await client.get('api/v1/trading-results/', params=params)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Данные по торгам за заданный период не найдены!'}


@pytest.mark.asyncio(loop_scope='session')
async def test_trading_last_results_404(client):
    """Проверка на 404, если данных нет"""
    params = {
        'limit': 5,
        'offset': 0,
        'oil_id': 'OIL999',
    }

    response = await client.get('api/v1/trading-results/last-trades', params=params)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Данные последних торгов не найдены!'}


@pytest.mark.asyncio(loop_scope='session')
async def test_trading_last_results_cached(client, trading_results, check_init_redis):
    """Проверяем кэширование и фильтрацию по oil_id"""

    params = {
        'limit': 5,
        'offset': 0,
        'oil_id': 'DT32',
    }

    r1 = await client.get('api/v1/trading-results/last-trades', params=params)
    r2 = await client.get('api/v1/trading-results/last-trades', params=params)

    assert r1.status_code == status.HTTP_200_OK
    assert r2.status_code == status.HTTP_200_OK

    def normalize_totals(records):
        for r in records:
            r['total'] = Decimal(r['total'])
        return records

    r1_data = normalize_totals(r1.json())
    r2_data = normalize_totals(r2.json())

    assert r1_data == r2_data
    assert len(r1.json()) == 1

    keys = await check_init_redis.keys('fastapi-cache:*')
    assert len(keys) > 0

    value = await check_init_redis.get(keys[0])
    assert value is not None


@pytest.mark.asyncio(loop_scope='session')
async def test_trading_last_results_pagination(client, trading_results):
    """Проверка limit, offset и фильтров"""

    params = {
        'limit': 1,
        'offset': 0,
        'oil_id': 'DT32',
    }
    response = await client.get('api/v1/trading-results/last-trades', params=params)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1

    params['offset'] = 1
    response = await client.get('api/v1/trading-results/last-trades', params=params)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Данные последних торгов не найдены!'}
