from pydantic import BaseModel, Field


class NevShareTrendQuery(BaseModel):
    years: int = Field(3, ge=1, le=10)
    granularity: str = Field("monthly", pattern="^(monthly|yearly)$")


class NevShareOverviewQuery(BaseModel):
    year: int = Field(..., ge=2000, le=2100)
    month: int = Field(..., ge=1, le=12)


class NevBreakdownQuery(BaseModel):
    years: int = Field(3, ge=1, le=10)
    granularity: str = Field("monthly", pattern="^(monthly|yearly)$")


class NevBreakdownDetailQuery(BaseModel):
    year: int = Field(..., ge=2000, le=2100)
    month: int = Field(..., ge=1, le=12)


class OriginShareTrendQuery(BaseModel):
    years: int = Field(3, ge=1, le=10)
    granularity: str = Field("monthly", pattern="^(monthly|yearly)$")
    data_type: str = Field("retail", pattern="^(retail|wholesale)$")


class OriginShareOverviewQuery(BaseModel):
    year: int = Field(..., ge=2000, le=2100)
    month: int = Field(..., ge=1, le=12)
    data_type: str = Field("retail", pattern="^(retail|wholesale)$")
