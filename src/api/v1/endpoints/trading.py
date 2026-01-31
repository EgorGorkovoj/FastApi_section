from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_cache.decorator import cache
from sqlalchemy.ext.asyncio import AsyncSession

from core.db_depends import get_async_session
from core.redis_utils import redis_fabcric
from crud.crud_trade import crud_trade
from schemas.filters import PaginationDep
from schemas.trading_schema import (
    LastTradesFilterSchema,
    ReadTradingSchema,
    TradingDynamicsFilterSchema,
)

router = APIRouter()


@router.get(
    '/trading-results/last-dates', status_code=status.HTTP_200_OK, response_model=list[date]
)
@cache(
    expire=redis_fabcric.create_cache().calculate_ttl_until_reset(),
    namespace='last-dates',
    key_builder=redis_fabcric.create_cache().build_key_from_request,
)
async def get_last_trading_dates(
    pagination: PaginationDep, session: AsyncSession = Depends(get_async_session)
) -> list[date]:
    """
    Возвращает список последних уникальных дат торгов.

    Назначение:
        - позволяет получить последние торговые дни.
        - кэшируется в Redis, чтобы снизить нагрузку на базу.

    Параметры:
        pagination (PaginationDep): Параметры пагинации
            (limit — количество элементов, offset — смещение).
        request (Request): HTTP-запрос (используется для формирования ключа кэша).
        session (AsyncSession): Асинхронная сессия SQLAlchemy.

    Возвращает:
        list[date]: Список последних уникальных дат торгов.

    Исключения:
        HTTPException 404: Если даты не найдены.
    """

    last_dates = await crud_trade.get_list_last_dates(session, pagination.limit, pagination.offset)
    if not last_dates:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Даты не найдены!')
    return last_dates


@router.get(
    '/trading-results/', status_code=status.HTTP_200_OK, response_model=list[ReadTradingSchema]
)
@cache(
    expire=redis_fabcric.create_cache().calculate_ttl_until_reset(),
    namespace='dynamics',
    key_builder=redis_fabcric.create_cache().build_key_from_request,
)
async def get_dynamics(
    pagination: PaginationDep,
    filters: TradingDynamicsFilterSchema = Depends(),
    session: AsyncSession = Depends(get_async_session),
) -> list[ReadTradingSchema]:
    """
    Возвращает список торгов за заданный период с возможностью фильтрации.

    Назначение:
        - получение данных торгов для анализа или отображения.
        - фильтрация по oil_id, delivery_type_id, delivery_basis_id и диапазону дат.
        - кэшируется в Redis, чтобы снизить нагрузку на базу.

    Параметры:
        pagination (PaginationDep): Параметры пагинации.
        filters (TradingDynamicsFilter): Параметры фильтрации:
            - oil_id (str): Идентификатор сырья.
            - delivery_type_id (str | None): Тип поставки (необязательный).
            - delivery_basis_id (str | None): Базис поставки (необязательный).
            - start_date (date): Начальная дата периода.
            - end_date (date): Конечная дата периода.
        session (AsyncSession): Асинхронная сессия SQLAlchemy.

    Возвращает:
        list[ReadTradingSchema]: Список торгов, подходящих под фильтры.

    Исключения:
        HTTPException 404: Если данные по торгам за период не найдены.
    """
    trades = await crud_trade.get_list_trade_for_period(
        session,
        filters.oil_id,
        filters.delivery_type_id,
        filters.delivery_basis_id,
        filters.start_date,
        filters.end_date,
        pagination.limit,
        pagination.offset,
    )
    if not trades:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Данные по торгам за заданный период не найдены!',
        )
    return trades


@router.get(
    '/trading-results/last-trades',
    status_code=status.HTTP_200_OK,
    response_model=list[ReadTradingSchema],
)
@cache(
    expire=redis_fabcric.create_cache().calculate_ttl_until_reset(),
    namespace='trading_results',
    key_builder=redis_fabcric.create_cache().build_key_from_request,
)
async def get_trading_results(
    pagination: PaginationDep,
    filters: LastTradesFilterSchema = Depends(),
    session: AsyncSession = Depends(get_async_session),
) -> list[ReadTradingSchema]:
    """
    Возвращает список последних торгов.

    Назначение:
        - получение последних доступных результатов торгов.
        - поддержка фильтрации по oil_id, delivery_type_id, delivery_basis_id.
        - кэшируется в Redis, чтобы снизить нагрузку на базу.

    Параметры:
        pagination (PaginationDep): Параметры пагинации.
        filters (TradingLastFilter): Параметры фильтрации:
            - oil_id (str): Идентификатор сырья.
            - delivery_type_id (str | None): Тип поставки (необязательный).
            - delivery_basis_id (str | None): Базис поставки (необязательный).
        session (AsyncSession): Асинхронная сессия SQLAlchemy.

    Возвращает:
        list[ReadTradingSchema]: Список последних торгов.

    Исключения:
        HTTPException 404: Если последние торги не найдены.
    """

    last_trades = await crud_trade.get_list_last_trades(
        session,
        filters.oil_id,
        filters.delivery_type_id,
        filters.delivery_basis_id,
        pagination.limit,
        pagination.offset,
    )
    if not last_trades:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Данные последних торгов не найдены!'
        )
    return last_trades
