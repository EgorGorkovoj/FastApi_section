import datetime
from itertools import islice
from typing import Any, Generator, Iterable, List

import pandas as pd
from crud.crud_trade import crud_trade
from crud.crud_state import crud_state
from models.trading_results import SpamixTradingResults
from parser_bulletin.parser_services.objects_converter import SpimexRowConverter
from sqlalchemy.ext.asyncio import AsyncSession


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

# TODO: Переписать докстринг
    async def save_table_bulk(
        self,
        df_list: list[tuple[pd.DataFrame, datetime.date]],
        # check_chunk_size: int = 2000,
        insert_batch_size: int = 2000,
    ) -> None:
        """
        Выполняет массовую загрузку данных из списка DataFrame в базу данных.

        Алгоритм:
            1. Итерирует все строки каждого DataFrame из списка.
            2. Конвертирует каждую строку в словарь данных модели через SpimexRowConverter.
            3. Устанавливает дату (file_date) для каждой записи.
            4. Проверяет существование записи по ключу (exchange_product_id, date) батчами.
            5. Формирует список только новых записей, которых ещё нет в БД.
            6. Массово сохраняет новые записи в БД через bulk_create() батчами.

        Параметры:
            df_list (list[tuple[pd.DataFrame, datetime.date]]): Список кортежей, где
                каждый кортеж содержит DataFrame с данными и дату file_date.
            check_chunk_size (int, optional): Размер батча при проверке существующих
                записей. По умолчанию 1000.
            insert_batch_size (int, optional): Размер батча при массовой вставке
                новых записей. По умолчанию 1000.

        Возвращает None.
        """
        objs_data: list[dict] = []
        last_load = await crud_state.get_last_state_load(
                self.session, self.source
            )
        max_loaded_date = None
        for df, file_date in df_list:
            if (
                last_load is not None
                and last_load.last_loaded_date is not None
                and file_date <= last_load.last_loaded_date
            ):
                continue
            if max_loaded_date is None or file_date > max_loaded_date:
                max_loaded_date = file_date
            # await crud_state.update_state_date(self.session, file_date)
            records = df.apply(
                lambda row: {**SpimexRowConverter.convert_to_dict(row), 'date': file_date}, axis=1
            ).tolist()
            objs_data.extend(records)

        for batch in self.chunked(objs_data, insert_batch_size):
            await self.crud.bulk_create(self.session, batch)
        # TODO: проверить!!!
        if max_loaded_date is not None:
            await crud_state.update_last_loaded_date(
                self.session, self.source, max_loaded_date
            )
        await crud_state.update_last_loaded_date(self.session, self.source, max_loaded_date)
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
