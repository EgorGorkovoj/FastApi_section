class LengthConstants:
    """
    Константы, задающие ограничения по длине
    для различных текстовых полей.

    Атрибуты:
        EXCHANGE_PRODUCT_ID_LENGTH (int): Максимальная длина
                                          идентификатора.
        EXCHANGE_PRODUCT_NAME_LENGTH (int): Максимальная длина
                                            полного названия инструмента.
        OIL_ID (int): Длина кода сырья.
        DELIVERY_BASIS_ID_LENGTH (int): Длина идентификатора базиса поставки.
        DELIVERY_BASIS_NAME_LENGTH (int): Максимальная длина названия
                                          базиса поставки.
        DELIVERY_TYPE_ID_LENGTH (int): Длина идентификатора типа поставки.
    """

    EXCHANGE_PRODUCT_ID_LENGTH: int = 24
    EXCHANGE_PRODUCT_NAME_LENGTH: int = 240
    OIL_ID_LENGTH: int = 4
    DELIVERY_BASIS_ID_LENGTH: int = 3
    DELIVERY_BASIS_NAME_LENGTH: int = 120
    DELIVERY_TYPE_ID_LENGTH: int = 1


class PriceConstants:
    """
    Базовый класс констант для цен.

    Атрибуты:
    - PRICE_NUMBER_OF_DIGITS (int): целая часть цены.
    - PRICE_FRACTIONAL_PART (int): сколько знаков после запятой у цены.
    """

    PRICE_NUMBER_OF_DIGITS: int = 14
    PRICE_FRACTIONAL_PART: int = 2


class TitleSchemaConstants:
    """
    Константы заголовков (title) для полей схемы
    результатов биржевых торгов.
    """

    EXCHANGE_PRODUCT_ID: str = 'Код инструмента'
    EXCHANGE_PRODUCT_NAME: str = 'Название инструмента'
    OIL_ID: str = 'Код нефтепродукта'
    DELIVERY_BASIS_ID: str = 'Код базиса поставки'
    DELIVERY_BASIS_NAME: str = 'Базис поставки'
    DELIVERY_TYPE_ID: str = 'Тип поставки'
    VOLUME: str = 'Объём договоров'
    TOTAL: str = 'Общая стоимость договоров'
    COUNT: str = 'Количество договоров'
    DATE: str = 'Дата торгов'


class DescriptionSchemaConstants:
    """Константы для описания полей схем Pydantic."""

    OIL_ID = 'Код типа нефтепродукта'
    DELIVERY_TYPE_ID = 'Идентификатор типа поставки (опционально)'
    DELIVERY_BASIS_ID = 'Идентификатор базиса поставки (опционально)'
    START_DATE = 'Дата начала периода для выборки торгов'
    END_DATE = 'Дата конца периода для выборки торгов'
    EXCHANGE_PRODUCT_ID = 'Уникальный идентификатор продукта на бирже'
    EXCHANGE_PRODUCT_NAME = 'Название продукта на бирже'
    DELIVERY_BASIS_NAME = 'Название основы поставки'
    VOLUME = 'Объем сделки'
    TOTAL = "Общая стоимость сделки"
    COUNT = 'Количество сделок'
    DATE = 'Дата торгов'
