import datetime

from sqlalchemy import between, desc, distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models import SpamixTradingResults

from .crud_base import CRUDBase


class TradeCRUD(CRUDBase):
    """
    Класс для работы с моделью 'SpamixTradingResults' через CRUD операции.
    Наследуется от CRUDBase, расширяя функциональность проверкой существующих записей.

    """

    async def get_max_date_trade(self, session: AsyncSession) -> datetime.date | None:
        """
        Получает максимальную дату торгов из таблицы SpamixTradingResults.

        Параметры:
            session (AsyncSession): Асинхронная сессия SQLAlchemy для работы с базой данных.

        Возвращает:
            datetime.date | None: Максимальная дата торгов, если записи есть в базе, иначе None.

        Примечание:
            Использует агрегатную функцию SQL 'MAX' для определения последней даты.
        """

        stmt = select(func.max(self.model.date))
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_list_last_dates(self, session: AsyncSession, limit: int | None, offset: int):
        """
        Возвращает список уникальных дат торгов, отсортированных
        по убыванию (от самых новых к старым).

        Используется для получения последних торговых дней.

        Параметры:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            limit (int | None): Максимальное количество дат.
                Если None — возвращаются все доступные даты.
            offset (int): Смещение (количество пропущенных записей).

        Возвращает:
            list[datetime.date]: Список уникальных дат торгов.
        """

        stmt = select(distinct(self.model.date)).order_by(desc(self.model.date))  # type: ignore
        if limit:
            stmt = self._apply_limit_offset(stmt, limit, offset)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_list_trade_for_period(
        self,
        session: AsyncSession,
        oil_id: str,
        delivery_type_id: str | None,
        delivery_basis_id: str | None,
        start_date: datetime.date,
        end_date: datetime.date,
        limit: int | None,
        offset: int,
    ) -> list[SpamixTradingResults]:
        """
        Возвращает список торгов за заданный период времени
        с возможностью фильтрации по параметрам.

        Обязательные условия:
            - oil_id
            - диапазон дат [start_date, end_date]

        Опциональные фильтры:
            - delivery_basis_id
            - delivery_type_id

        Результаты сортируются по возрастанию даты торгов.

        Параметры:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            oil_id (str): Код нефтепродукта.
            delivery_type_id (str | None): Тип поставки (опционально).
            delivery_basis_id (str | None): Базис поставки (опционально).
            start_date (date): Дата начала периода.
            end_date (date): Дата окончания периода.
            limit (int | None): Максимальное количество записей.
                Если None — возвращаются все записи.
            offset (int): Смещение для пагинации.

        Возвращает:
            list[SpamixTradingResults]: Список торговых записей
            за указанный период.
        """

        conditions = [
            self.model.oil_id == oil_id,
            between(self.model.date, start_date, end_date),
        ]
        if delivery_basis_id is not None:
            conditions.append(self.model.delivery_basis_id == delivery_basis_id)
        if delivery_type_id is not None:
            conditions.append(self.model.delivery_type_id == delivery_type_id)

        stmt = select(self.model).where(*conditions).order_by(self.model.date)
        if limit:
            stmt = self._apply_limit_offset(stmt, limit, offset)
        result = await session.execute(stmt)
        return result.scalars().all()  # type: ignore

    async def get_list_last_trades(
        self,
        session: AsyncSession,
        oil_id: str,
        delivery_type_id: str | None,
        delivery_basis_id: str | None,
        limit: int | None,
        offset: int,
    ) -> list[SpamixTradingResults]:
        """
        Возвращает список последних торгов по заданному нефтепродукту
        с возможностью дополнительной фильтрации.

        Обязательное условие:
            - oil_id

        Опциональные фильтры:
            - delivery_basis_id
            - delivery_type_id

        Результаты сортируются по дате торгов в порядке убывания
        (сначала самые новые).

        Параметры:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            oil_id (str): Код нефтепродукта.
            delivery_type_id (str | None): Тип поставки (опционально).
            delivery_basis_id (str | None): Базис поставки (опционально).
            limit (int | None): Максимальное количество записей.
                Если None — возвращаются все записи.
            offset (int): Смещение для пагинации.

        Возвращает:
            list[SpamixTradingResults]: Список последних торгов.
        """

        conditions = [
            self.model.oil_id == oil_id,
        ]

        if delivery_basis_id is not None:
            conditions.append(self.model.delivery_basis_id == delivery_basis_id)
        if delivery_type_id is not None:
            conditions.append(self.model.delivery_type_id == delivery_type_id)

        stmt = select(self.model).where(*conditions).order_by(desc(self.model.date))
        if limit:
            stmt = self._apply_limit_offset(stmt, limit, offset)
        result = await session.execute(stmt)
        return result.scalars().all()  # type: ignore


crud_trade = TradeCRUD(SpamixTradingResults)
