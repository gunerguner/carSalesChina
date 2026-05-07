from pydantic import BaseModel
from typing import Optional


class OverviewQuery(BaseModel):
    year: int
    month: int
    energy_type: Optional[str] = "all"


class TrendQuery(BaseModel):
    energy_type: str = "all"
    years: int = 3
    granularity: str = "monthly"


class CompareQuery(BaseModel):
    energy_type: str = "all"
    start_year: int
    start_month: int
    end_year: int
    end_month: int


class YearlyQuery(BaseModel):
    year: int
    energy_type: str = "all"


class ByEnergyTypeQuery(BaseModel):
    year: int
    month: int


class BySegmentQuery(BaseModel):
    year: int
    month: int