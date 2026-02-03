import pytest
from fastapi import status

from src.crud.crud_trade import crud_trade


@pytest.mark.asyncio
async def test_last_dates_404(client):
    response = await client.get('api/v1/trading-results/last-dates?limit=5&offset=0')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Даты не найдены!'}


@pytest.mark.asyncio
async def test_last_dates_cached(trading_results, client, mocker):
    spy = mocker.spy(crud_trade, 'get_list_last_dates')

    r1 = await client.get('api/v1/trading-results/last-dates?limit=5&offset=0')
    r2 = await client.get('api/v1/trading-results/last-dates?limit=5&offset=0')

    assert r1.status_code == status.HTTP_200_OK
    assert r2.status_code == status.HTTP_200_OK

    assert r1.json() == r2.json()
    assert len(r1.json()) == 2

    assert spy.call_count == 1


@pytest.mark.skip
async def test_last_dates_pagination(client, trading_results):
    """Проверяем пагинацию"""

    response = await client.get('api/v1/trading-results/last-dates?limit=1&offset=0')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    print(trading_results[0])
    assert response.json()[0] == trading_results[0].date.isoformat()

    response = await client.get('api/v1/trading-results/last-dates?limit=1&offset=1')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0] == trading_results[1].date.isoformat()


@pytest.mark.skip
async def test_trading_dynamics_404(client):
    """Проверка на 404, если данных нет"""
    params = {
        'limit': 5,
        'offset': 0,
        'oil_id': 'OIL999',
        'delivery_type_id': None,
        'delivery_basis_id': None,
        'start_date': '2024-01-01',
        'end_date': '2024-01-31',
    }

    response = await client.get('api/v1/trading-results/', params=params)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Данные по торгам за заданный период не найдены!'}


@pytest.mark.skip
async def test_trading_dynamics_cached(client, trading_results, mocker):
    """Проверяем кэширование и фильтрацию по oil_id"""
    spy = mocker.spy(crud_trade, 'get_list_trade_for_period')

    params = {
        'limit': 5,
        'offset': 0,
        'oil_id': 'DT32',
        'delivery_type_id': None,
        'delivery_basis_id': None,
        'start_date': '2023-02-01',
        'end_date': '2025-11-28',
    }

    r1 = await client.get('api/v1/trading-results/', params=params)
    r2 = await client.get('api/v1/trading-results/', params=params)

    assert r1.status_code == status.HTTP_200_OK
    assert r2.status_code == status.HTTP_200_OK

    assert r1.json() == r2.json()
    assert len(r1.json()) == 1

    assert spy.call_count == 1


@pytest.mark.skip
async def test_trading_dynamics_pagination(client, trading_results):
    """Проверка limit, offset и фильтров"""

    params = {
        'limit': 1,
        'offset': 0,
        'oil_id': 'DT32',
        'delivery_type_id': None,
        'delivery_basis_id': None,
        'start_date': '2023-02-01',
        'end_date': '2025-11-28',
    }
    response = await client.get('api/v1/trading-results/', params=params)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1

    params['offset'] = 1
    response = await client.get('api/v1/trading-results/', params=params)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert len(response.json()) == 0


@pytest.mark.skip
async def test_trading_last_results_404(client):
    """Проверка на 404, если данных нет"""
    params = {
        'limit': 5,
        'offset': 0,
        'oil_id': 'OIL999',
        'delivery_type_id': None,
        'delivery_basis_id': None,
    }

    response = await client.get('api/v1/trading-results/last-trades', params=params)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Данные последних торгов не найдены!'}


@pytest.mark.skip
async def test_trading_last_results_cached(client, trading_results, mocker):
    """Проверяем кэширование и фильтрацию по oil_id"""
    spy = mocker.spy(crud_trade, 'get_list_last_trades')

    params = {
        'limit': 5,
        'offset': 0,
        'oil_id': 'DT32',
        'delivery_type_id': None,
        'delivery_basis_id': None,
    }

    r1 = await client.get('api/v1/trading-results/last-trades', params=params)
    r2 = await client.get('api/v1/trading-results/last-trades', params=params)

    assert r1.status_code == status.HTTP_200_OK
    assert r2.status_code == status.HTTP_200_OK

    assert r1.json() == r2.json()
    assert len(r1.json()) == 1

    assert spy.call_count == 1


@pytest.mark.skip
async def test_trading_last_results_pagination(client, trading_results):
    """Проверка limit, offset и фильтров"""

    params = {
        'limit': 1,
        'offset': 0,
        'oil_id': 'DT32',
        'delivery_type_id': None,
        'delivery_basis_id': None,
    }
    response = await client.get('api/v1/trading-results/last-trades', params=params)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1

    params['offset'] = 1
    response = await client.get('api/v1/trading-results/', params=params)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert len(response.json()) == 0
