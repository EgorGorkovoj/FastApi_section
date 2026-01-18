import datetime

from models import ParserState

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger import logger

from .crud_base import CRUDBase


class StateCRUD(CRUDBase):

    async def get_last_state_load(
        self, session: AsyncSession, db_name: str
    ) -> ParserState | None:
        stmt = select(self.model).where(self.model.source == db_name)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_last_loaded_date(
        self,
        session: AsyncSession,
        db_name: str,
        new_date: datetime.date,
    ) -> None:
        state = await self.get_last_state_load(session, db_name)

        try:
            if state:
                state.last_loaded_date = new_date
            else:
                session.add(
                    self.model(
                        source=db_name,
                        last_loaded_date=new_date,
                    )
                )
            await session.commit()
        except SQLAlchemyError as error:
            await session.rollback()
            logger.error(
                'Произошла ошибка при создании или обновлении данных в '
                f'{self.model.__name__}: {error}!'  # type: ignore
            )
            raise


crud_state = StateCRUD(ParserState)
