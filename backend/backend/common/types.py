from typing import Literal, TypedDict

DataType = Literal["retail", "production"]
DateType = Literal["monthly", "quarterly", "yearly"]
LevelType = Literal["all", "nev", "bev"]
Granularity = Literal["monthly", "yearly"]


class MarketRawRow(TypedDict):
    year: int
    month: int
    data_type: str
    level_type: str
    sales: float


class BrandMetaRow(TypedDict):
    brand_id: int
    brand_name: str


class BrandMonthlyPoint(TypedDict):
    year: int
    month: int
    sales: float


class BrandTrendSeries(TypedDict):
    brand_name: str
    monthly_data: list[BrandMonthlyPoint]


class SalesUpsertRow(TypedDict):
    year: int
    month: int
    sales: float
    data_type: str
    date_type: str
    level_type: str


class BrandSalesUpsertRow(TypedDict):
    year: int
    month: int
    brand_id: int
    sales_volume: float | None
    data_type: str
    date_type: str
    level_type: str


class OriginShareUpsertRow(TypedDict):
    year: int
    month: int
    origin: str
    sales_volume: float


class OverallSalesRecord(TypedDict):
    year: int
    month: int
    sales: float
    data_type: str
    date_type: str
    level_type: str


class BrandSalesRecord(TypedDict):
    year: int
    month: int
    master_id: int
    sales_volume: float
    data_type: str
    date_type: str
    level_type: str
