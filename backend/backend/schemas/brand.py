from pydantic import BaseModel, Field


class TrendAllPeriodsQuery(BaseModel):
    brand_names: str = Field(...)
    data_type: str = Field("retail", pattern="^(retail|production)$")
