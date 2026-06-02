from pydantic import BaseModel, Field

from backend.common.types import Granularity


class AnalysisTrendQuery(BaseModel):
    years: int = Field(3, ge=1, le=10)
    granularity: Granularity = "monthly"
