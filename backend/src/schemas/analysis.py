from pydantic import BaseModel
from typing import Optional


class NevShareTrendQuery(BaseModel):
    years: int = 3
    granularity: str = "monthly"


class NevShareOverviewQuery(BaseModel):
    year: int
    month: int


class NevBreakdownQuery(BaseModel):
    years: int = 3
    granularity: str = "monthly"


class NevBreakdownDetailQuery(BaseModel):
    year: int
    month: int