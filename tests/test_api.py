import json
from datetime import date
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_last_dates_in_db(
    client: AsyncClient, override_redis: AsyncMock, override_session: AsyncMock
):
    fake_dates = [date(2024, 1, 1), date(2024, 1, 2)]

    with patch(
        'src.api.v1.endpoints.trading.crud_trade.get_list_last_dates', new_callable=AsyncMock
    ) as mock_list_dates:
        mock_list_dates.return_value = fake_dates
        response = await client.get('/api/v1/trading-results/last-dates?limit=2&offset=0')

    assert response.status_code == 200
    assert response.json() == ['2024-01-01', '2024-01-02']
    override_redis.set.assert_awaited_once()


@pytest.mark.asyncio
async def test_last_dates_from_cache(client: AsyncClient, override_redis: AsyncMock):
    override_redis.get.return_value = '["2024-01-01"]'

    response = await client.get('/api/v1/trading-results/last-dates?limit=1&offset=0')
    assert response.status_code == 200
    assert response.json() == ['2024-01-01']


@pytest.mark.parametrize(
    'limit, offset',
    [
        (1, 0),
        (2, 0),
        (1, 1),
        (5, 0),
    ],
)
@pytest.mark.asyncio
async def test_last_dates_pagination(
    limit: int,
    offset: int,
    client: AsyncClient,
    override_redis: AsyncMock,
    override_session: AsyncMock,
):
    all_dates = [
        date(2024, 1, 1),
        date(2024, 1, 2),
        date(2024, 1, 3),
    ]

    async def fake_get_list_last_dates(session, limit, offset):
        return all_dates[offset : offset + limit]

    with patch(
        'src.api.v1.endpoints.trading.crud_trade.get_list_last_dates',
        side_effect=fake_get_list_last_dates,
    ) as mock_list_dates:
        response = await client.get(
            f'/api/v1/trading-results/last-dates?limit={limit}&offset={offset}'
        )

        assert response.status_code == 200
        assert len(response.json()) == len(all_dates[offset : offset + limit])

        mock_list_dates.assert_awaited_once_with(override_session, limit, offset)


@pytest.mark.asyncio
async def test_dynamics_trades_in_db(
    client: AsyncClient, override_redis: AsyncMock, override_session: AsyncMock, fake_trade: type
):
    trade = fake_trade(1)
    fake_trades = [trade.to_dict()]

    with patch(
        'src.api.v1.endpoints.trading.crud_trade.get_list_trade_for_period', new_callable=AsyncMock
    ) as mock_crud:
        mock_crud.return_value = fake_trades

        response = await client.get(
            '/api/v1/trading-results/'
            '?oil_id=A1'
            '&start_date=2024-01-01'
            '&end_date=2024-01-31'
            '&limit=10'
            '&offset=0'
        )

        assert response.status_code == 200
        assert response.json() == fake_trades

        mock_crud.assert_awaited_once()
        override_redis.set.assert_awaited_once()


@pytest.mark.asyncio
async def test_dynamics_trades_from_cache(
    client: AsyncClient, override_redis: AsyncMock, fake_trade: type
):
    trade = fake_trade(1)
    fake_data = [trade.to_dict()]

    override_redis.get.return_value = json.dumps(fake_data)

    response = await client.get(
        '/api/v1/trading-results/'
        '?oil_id=A1'
        '&start_date=2024-01-01'
        '&end_date=2024-01-31'
        '&limit=10'
        '&offset=0'
    )
    assert response.status_code == 200
    assert response.json() == fake_data


@pytest.mark.parametrize(
    'limit, offset, expected_count',
    [
        (1, 0, 1),
        (2, 0, 2),
        (3, 1, 2),
        (5, 0, 3),
    ],
)
@pytest.mark.asyncio
async def test_get_dynamics_pagination(
    limit: int,
    offset: int,
    expected_count: int,
    client: AsyncClient,
    override_redis: AsyncMock,
    override_session: AsyncMock,
    fake_trade: type,
):
    all_trades = [fake_trade(i) for i in range(3)]

    async def fake_get_list_trade_for_period(
        session,
        oil_id,
        delivery_type_id,
        delivery_basis_id,
        start_date,
        end_date,
        limit_arg,
        offset_arg,
    ):
        return all_trades[offset_arg : offset_arg + limit_arg]

    with patch(
        'src.api.v1.endpoints.trading.crud_trade.get_list_trade_for_period',
        side_effect=fake_get_list_trade_for_period,
    ) as mock_crud:
        response = await client.get(
            f'/api/v1/trading-results/'
            f'?oil_id=A0'
            f'&start_date=2024-01-01'
            f'&end_date=2024-01-31'
            f'&limit={limit}'
            f'&offset={offset}'
        )

        assert response.status_code == 200
        assert len(response.json()) == expected_count

        mock_crud.assert_awaited_once_with(
            override_session, 'A0', None, None, date(2024, 1, 1), date(2024, 1, 31), limit, offset
        )

        override_redis.set.assert_awaited_once()


@pytest.mark.asyncio
async def test_last_trades_from_db(
    client: AsyncClient, override_redis: AsyncMock, override_session: AsyncMock, fake_trade: type
):
    trade = fake_trade(1)
    fake_trades = [trade.to_dict()]

    with patch(
        'src.api.v1.endpoints.trading.crud_trade.get_list_last_trades', new_callable=AsyncMock
    ) as mock_crud:
        mock_crud.return_value = fake_trades
        response = await client.get(
            '/api/v1/trading-results/last-trades?limit=1&offset=0&oil_id=A1'
        )
        assert response.status_code == 200
        assert len(response.json()) == 1
        mock_crud.assert_awaited_once_with(override_session, 'A1', None, None, 1, 0)
        override_redis.set.assert_awaited_once()


@pytest.mark.asyncio
async def test_last_trades_from_cache(
    client: AsyncClient, override_redis: AsyncMock, fake_trade: type
):
    trade = fake_trade(1)
    fake_data = [trade.to_dict()]

    override_redis.get.return_value = json.dumps(fake_data)

    response = await client.get(
        '/api/v1/trading-results/last-trades' '?oil_id=A1' '&limit=10' '&offset=0'
    )

    assert response.status_code == 200
    assert response.json() == fake_data


@pytest.mark.parametrize(
    'limit, offset, expected_count',
    [
        (1, 0, 1),
        (2, 0, 2),
        (3, 1, 2),
        (5, 0, 3),
    ],
)
@pytest.mark.asyncio
async def test_last_trades_pagination(
    limit: int,
    offset: int,
    expected_count: int,
    client: AsyncClient,
    override_redis: AsyncMock,
    override_session: AsyncMock,
    fake_trade: type,
):
    all_trades = [fake_trade(i) for i in range(3)]

    async def fake_get_list_trade_for_period(
        session, oil_id, delivery_type_id, delivery_basis_id, limit_arg, offset_arg
    ):
        return all_trades[offset_arg : offset_arg + limit_arg]

    with patch(
        'src.api.v1.endpoints.trading.crud_trade.get_list_last_trades',
        side_effect=fake_get_list_trade_for_period,
    ) as mock_crud:
        response = await client.get(
            f'/api/v1/trading-results/last-trades'
            f'?oil_id=A0'
            f'&limit={limit}'
            f'&offset={offset}'
        )

        assert response.status_code == 200
        assert len(response.json()) == expected_count

        mock_crud.assert_awaited_once_with(override_session, 'A0', None, None, limit, offset)

        override_redis.set.assert_awaited_once()
