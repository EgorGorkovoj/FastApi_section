import datetime

from core.config import settings
from core.db_depends import AsyncSessionLocal
from core.logger import logger
from crud.crud_trade import crud_trade
from parser_bulletin.parser_main import parser_main


async def check_last_date_parser_spmx() -> None:
    """
    Проверяет последнюю дату торгов в базе и запускает парсер Spimex при необходимости.

    Логика работы:
        1. Получает сегодняшнюю дату.
        2. Проверяет последнюю дату торгов, сохранённую в базе данных.
        3. Если последние данные уже содержат сегодняшнюю дату или позже —
           парсер не запускается.
        4. Если данных нет или они устарели:
            - Определяется дата начала парсинга:
                * Если данных нет — используется DEFAULT_START_DATE из настроек.
                * Иначе — день после последней даты в БД.
            - Вызывается 'parser_main' для загрузки и обработки данных
              до текущей даты включительно.

    Применение:
        - Вызывается при старте сервера FastAPI для поддержания базы актуальной.
        - Позволяет избежать повторного парсинга уже загруженных данных.

    Возвращает:
        None
    """

    logger.info('Задача запуска парсера инициирована')
    today = datetime.date.today()
    async with AsyncSessionLocal() as session:
        max_date_trade: datetime.date | None = await crud_trade.get_max_date_trade(session=session)
    logger.info(f'Последняя дата торгов в БД: {max_date_trade}')
    if max_date_trade and max_date_trade >= today:
        return

    if max_date_trade is None:
        start_date = settings.DEFAULT_START_DATE
    else:
        start_date = max_date_trade + datetime.timedelta(days=1)

    await parser_main(
        start_date=start_date,
        end_date=today,
    )
