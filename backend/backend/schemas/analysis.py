from pydantic import BaseModel, Field


class NevShareTrendQuery(BaseModel):
    years: int = Field(3, ge=1, le=10)
    granularity: str = Field("monthly", pattern="^(monthly|yearly)$")


class NevBreakdownQuery(BaseModel):
    years: int = Field(3, ge=1, le=10)
    granularity: str = Field("monthly", pattern="^(monthly|yearly)$")


class OriginShareTrendQuery(BaseModel):
    years: int = Field(3, ge=1, le=10)
    granularity: str = Field("monthly", pattern="^(monthly|yearly)$")
    data_type: str = Field("retail", pattern="^(retail|wholesale)$")
