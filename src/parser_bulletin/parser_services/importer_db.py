import datetime
from itertools import islice
from typing import Any, Generator, Iterable, List

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from crud.crud_trade import crud_trade
from models.trading_results import SpamixTradingResults
from parser_bulletin.parser_services.objects_converter import SpimexRowConverter


class SpimexImporterDB:
    """
    Класс для импорта данных таблиц в базу данных.

    Отвечает за:
        - конвертацию строк pandas.DataFrame в формат ORM-модели;
        - проверку существования записей в БД;
        - вставку одиночных строк или массовую загрузку;
        - работу через CRUD-слой (TradeCRUD).

    Параметры:
        session (Session): Активная сессия SQLAlchemy, в рамках которой
            выполняются операции записи и проверки.
    """

    source: str = SpamixTradingResults.__tablename__

    def __init__(self, session: AsyncSession):
        self.session = session
        self.crud = crud_trade

    async def save_table_bulk(
        self,
        df_list: list[tuple[pd.DataFrame, datetime.date]],
        insert_batch_size: int = 2000,
    ) -> None:
        """
        Массово сохраняет новые записи из DataFrame в базу, пропуская уже существующие по дате.

        Для каждой записи используется дата файла (file_date) и проверяется,
        не содержится ли она уже в базе (через max_loaded_date).
        Только записи с датой позже max_loaded_date добавляются в список для вставки.

        Данные сохраняются батчами указанного размера (insert_batch_size) с помощью bulk_create.

        Параметры:
            df_list (list[tuple[pd.DataFrame, datetime.date]]): Список кортежей, где каждый
                кортеж содержит DataFrame с данными и дату file_date.
            insert_batch_size (int, optional): Размер батча для массовой вставки.
                                               По умолчанию 2000.

        Возвращает:
            None
        """
        objs_data: list[dict] = []
        max_loaded_date = await self.crud.get_max_date_trade(self.session)

        for df, file_date in df_list:
            if max_loaded_date is not None and max_loaded_date >= file_date:
                continue

            records = df.apply(
                lambda row: {**SpimexRowConverter.convert_to_dict(row), 'date': file_date}, axis=1
            ).tolist()
            objs_data.extend(records)

        for batch in self.chunked(objs_data, insert_batch_size):
            await self.crud.bulk_create(self.session, batch)

        return None

    @staticmethod
    def chunked(iterable: Iterable, size: int) -> Generator[List[Any], None, None]:
        """
        Разбивает итерируемый объект на чанки заданного размера.

        Алгоритм:
            1. Создаёт итератор из переданного объекта.
            2. Последовательно извлекает элементы по 'size' штук.
            3. Возвращает каждый чанк как список через генератор.
            4. Останавливается, когда элементы заканчиваются.

        Параметры:
            iterable (Iterable): Любой итерируемый объект (список, множество, генератор и т.п.).
            size (int): Размер чанка (количество элементов в одном куске).

        Возвращает:
            Generator[list]: Генератор списков, каждый из которых содержит до 'size' элементов.
        """
        it = iter(iterable)
        while True:
            chunk = list(islice(it, size))
            if not chunk:
                break
            yield chunk
