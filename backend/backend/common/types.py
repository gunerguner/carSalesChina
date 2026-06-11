from typing import Literal, TypedDict

DataType = Literal["retail", "production"]
DateType = Literal["monthly", "quarterly", "yearly"]
LevelType = Literal["all", "nev", "bev"]
Granularity = Literal["monthly", "yearly"]


class MarketRawRow(TypedDict):
    year: int
    month: int
    data_type: DataType
    level_type: LevelType
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


class BrandSalesUpsertRow(TypedDict):
    year: int
    month: int
    brand_id: int
    sales_volume: float | None
    data_type: DataType
    date_type: DateType
    level_type: LevelType


class OriginShareUpsertRow(TypedDict):
    year: int
    month: int
    origin: str
    sales_volume: float


class OverallSalesRecord(TypedDict):
    year: int
    month: int
    sales: float
    data_type: DataType
    date_type: DateType
    level_type: LevelType


class BrandSalesRecord(TypedDict):
    year: int
    month: int
    master_id: int
    sales_volume: float
    data_type: DataType
    date_type: DateType
    level_type: LevelType


class AnalysisPeriodRow(TypedDict, total=False):
    year: int
    month: int


class NevShareTrendRow(AnalysisPeriodRow):
    nev_penetration_rate: float
    total_sales: float
    nev_sales: float


class NevBreakdownRow(AnalysisPeriodRow):
    nev_sales: float
    bev_sales: float
    bev_ratio: float
    phev_sales: float
    phev_ratio: float
    hybrid_sales: float
    hybrid_ratio: float


class OriginShareTrendRow(AnalysisPeriodRow):
    domestic: float
    german: float
    japanese: float
    american: float
    european: float
    french: float
    korean: float
