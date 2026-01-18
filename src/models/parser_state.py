from datetime import date
from sqlalchemy import Date, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ParserState(Base):
    """
    Модель ORM, представляющая состояние выполнения парсера данных.

    Используется для хранения служебной информации о том,
    был ли запущен парсер конкретного источника данных и
    до какого момента данные были успешно загружены в БД.

    Назначение:
        - предотвращение повторного парсинга уже загруженных данных
        - возможность докачки только новых данных
        - хранение контрольной точки (checkpoint) парсинга

    Поля:
        source (str): Уникальный идентификатор источника данных
            или парсера (например: 'exchange_bulletin').
            Используется для различения состояний разных парсеров.

        last_loaded_date (datetime.date | None): Дата,
            по которую данные были успешно загружены.
            Используется как точка старта для последующих запусков
            парсера. Может быть None при первом запуске.

        created_on (datetime): Дата и время создания записи
            о состоянии парсера (устанавливается автоматически).

        updated_on (datetime): Дата и время последнего обновления
            состояния парсера (обновляется автоматически).
    """

    source: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    last_loaded_date: Mapped[date | None] = mapped_column(Date, nullable=True)
