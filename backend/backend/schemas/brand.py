from pydantic import BaseModel
from typing import Optional


class RankingQuery(BaseModel):
    year: int
    month: int
    page: int = 1
    pageSize: int = 20
    is_nev: Optional[int] = None


class YearlyRankingQuery(BaseModel):
    year: int
    page: int = 1
    pageSize: int = 20


class CompareQuery(BaseModel):
    brand_ids: str
    year: int
    month: int


class CompareTrendQuery(BaseModel):
    brand_ids: str
    years: int = 3
    granularity: str = "monthly"


class BrandDetailQuery(BaseModel):
    year: int
    month: int


class BrandTrendQuery(BaseModel):
    years: int = 3
    granularity: str = "monthly"