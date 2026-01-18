import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from crud.crud_state import crud_state
from models.trading_results import SpamixTradingResults
from parser_bulletin.parser_main import parser_main

# TODO: нужно сделать логику получше, плюс логика пре --reload, чтобы не парсило.
async def check_last_date_parser_spmx(session: AsyncSession) -> None:
    today = datetime.date.today()
    state_spmx = await crud_state.get_last_state_load(
        session, SpamixTradingResults.__tablename__
    )

    if state_spmx is None or state_spmx.last_loaded_date is None:
        await parser_main(datetime.date(2023, 1, 1), end_date=today)
        return None

    if state_spmx.last_loaded_date >= today:
        return None

    start_date = state_spmx.last_loaded_date + datetime.timedelta(days=1)
    await parser_main(start_date, end_date=today)
