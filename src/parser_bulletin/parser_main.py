import asyncio
import datetime

from core.logger import logger
from .parser_services.decorators import measure_time
from parser_bulletin.runner import SpimexParserRun


@measure_time
async def parser_main(
    start_date: datetime.date, end_date: datetime.date
) -> None:
    runner = SpimexParserRun(
        start_date=start_date,
        end_date=end_date,
    )
    try:
        await runner.run()
    except Exception as e:
        logger.error(f'Произошла ошибка {e} в работе парсера!')


if __name__ == '__main__':
    start_date = datetime.date(2023, 1, 1)
    end_date = datetime.date.today()

    asyncio.run(parser_main(start_date=start_date, end_date=end_date))
