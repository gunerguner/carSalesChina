from pydantic import BaseModel, Field


class RankingQuery(BaseModel):
    year: int = Field(..., ge=2000, le=2100)
    month: int = Field(..., ge=1, le=12)
    page: int = Field(1, ge=1)
    pageSize: int = Field(20, ge=1, le=100)
    data_type: str = Field("retail", pattern="^(retail|wholesale|production)$")


class YearlyRankingQuery(BaseModel):
    year: int = Field(..., ge=2000, le=2100)
    page: int = Field(1, ge=1)
    pageSize: int = Field(20, ge=1, le=100)
    data_type: str = Field("retail", pattern="^(retail|wholesale|production)$")


class CompareTrendQuery(BaseModel):
    brand_names: str = Field(...)
    years: int = Field(3, ge=1, le=10)
    granularity: str = Field("monthly", pattern="^(monthly|yearly)$")
    data_type: str = Field("retail", pattern="^(retail|wholesale|production)$")
