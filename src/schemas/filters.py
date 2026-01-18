from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """
    Параметры пагинации для запросов с ограничением и смещением.

    Поля:
        limit (int): Количество элементов на странице.
        offset (int): Смещение (количество пропущенных записей).
    """

    limit: int | None = Field(
        None, title='Лимит', description='Количество элементов на странице'
    )
    offset: int = Field(
        0, ge=0, title='Пропуск записей', description='Смещение для пагинации'
    )


# Зависимость для пагинации.
PaginationDep = Annotated[PaginationParams, Depends(PaginationParams)]
