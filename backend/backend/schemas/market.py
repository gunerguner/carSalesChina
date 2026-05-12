from pydantic import BaseModel, Field


class OverviewQuery(BaseModel):
    year: int = Field(..., ge=2000, le=2100)
    month: int = Field(..., ge=0, le=12)
    data_type: str = Field("retail", pattern="^(retail|production)$")
    date_type: str = Field("monthly", pattern="^(monthly|quarterly|yearly)$")
    level_type: str = Field("all", pattern="^(all|nev|bev)$")


class TrendQuery(BaseModel):
    years: int = Field(3, ge=1, le=10)
    granularity: str = Field("monthly", pattern="^(monthly|yearly)$")
    data_type: str = Field("retail", pattern="^(retail|production)$")
    date_type: str = Field("monthly", pattern="^(monthly|quarterly|yearly)$")
    level_type: str = Field("all", pattern="^(all|nev|bev)$")


class YearlyQuery(BaseModel):
    year: int = Field(..., ge=2000, le=2100)
    data_type: str = Field("retail", pattern="^(retail|production)$")
    date_type: str = Field("monthly", pattern="^(monthly|quarterly|yearly)$")
    level_type: str = Field("all", pattern="^(all|nev|bev)$")