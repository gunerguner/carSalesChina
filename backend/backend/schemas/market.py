from pydantic import BaseModel, Field


class OverviewQuery(BaseModel):
    year: int = Field(..., ge=2000, le=2100)
    month: int = Field(..., ge=1, le=12)
    energy_type: str = Field("all")
    data_type: str = Field("retail", pattern="^(retail|wholesale|production)$")


class TrendQuery(BaseModel):
    energy_type: str = Field("all")
    years: int = Field(3, ge=1, le=10)
    granularity: str = Field("monthly", pattern="^(monthly|yearly)$")
    data_type: str = Field("retail", pattern="^(retail|wholesale|production)$")


class CompareQuery(BaseModel):
    energy_type: str = Field("all")
    start_year: int = Field(..., ge=2000, le=2100)
    start_month: int = Field(..., ge=1, le=12)
    end_year: int = Field(..., ge=2000, le=2100)
    end_month: int = Field(..., ge=1, le=12)
    data_type: str = Field("retail", pattern="^(retail|wholesale|production)$")


class YearlyQuery(BaseModel):
    year: int = Field(..., ge=2000, le=2100)
    energy_type: str = Field("all")
    data_type: str = Field("retail", pattern="^(retail|wholesale|production)$")
