import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from core.constants import TitleSchemaConstants, DescriptionSchemaConstants


class BaseTradingSchema(BaseModel):
    """Базовая схема для чтения данных из БД результатов торгов."""
    oil_id: str = Field(
        ..., title=TitleSchemaConstants.OIL_ID, description=DescriptionSchemaConstants.OIL_ID
    )


class LastTradesFilterSchema(BaseTradingSchema):
    """Общие поля фильтров для торгов."""
    delivery_type_id: str | None = Field(
        None,
        title=TitleSchemaConstants.DELIVERY_TYPE_ID,
        description=DescriptionSchemaConstants.DELIVERY_TYPE_ID
    )
    delivery_basis_id: str | None = Field(
        None, title=TitleSchemaConstants.DELIVERY_BASIS_ID,
        description=DescriptionSchemaConstants.DELIVERY_BASIS_ID
    )


class TradingDynamicsFilterSchema(LastTradesFilterSchema):
    """Фильтр для динамики торгов по заданному периоду."""
    start_date: datetime.date = Field(..., description=DescriptionSchemaConstants.START_DATE)
    end_date: datetime.date = Field(..., description=DescriptionSchemaConstants.END_DATE)


class ReadTradingSchema(BaseTradingSchema):
    """Схема для чтения полных данных из БД результатов торгов."""
    exchange_product_id: str = Field(
        ...,
        title=TitleSchemaConstants.EXCHANGE_PRODUCT_ID,
        description=DescriptionSchemaConstants.EXCHANGE_PRODUCT_ID
    )
    exchange_product_name: str = Field(
        ...,
        title=TitleSchemaConstants.EXCHANGE_PRODUCT_NAME,
        description=DescriptionSchemaConstants.EXCHANGE_PRODUCT_NAME
    )
    delivery_basis_id: str = Field(
        ...,
        title=TitleSchemaConstants.DELIVERY_BASIS_ID,
        description=DescriptionSchemaConstants.DELIVERY_BASIS_ID
    )
    delivery_basis_name: str = Field(
        ...,
        title=TitleSchemaConstants.DELIVERY_BASIS_NAME,
        description=DescriptionSchemaConstants.DELIVERY_BASIS_NAME
    )
    delivery_type_id: str = Field(
        ...,
        title=TitleSchemaConstants.DELIVERY_TYPE_ID,
        description=DescriptionSchemaConstants.DELIVERY_TYPE_ID
    )
    volume: int | None = Field(
        None, title=TitleSchemaConstants.VOLUME, description=DescriptionSchemaConstants.VOLUME
    )
    total: Decimal = Field(
        ..., title=TitleSchemaConstants.TOTAL, description=DescriptionSchemaConstants.TOTAL
    )
    count: int | None = Field(
        None, title=TitleSchemaConstants.COUNT, description=DescriptionSchemaConstants.COUNT
    )
    date: datetime.date = Field(
        ..., title=TitleSchemaConstants.DATE, description=DescriptionSchemaConstants.DATE
    )

    model_config = ConfigDict(from_attributes=True)
