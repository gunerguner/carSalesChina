from typing import Literal

from pydantic import BaseModel, Field


class AnalysisTrendQuery(BaseModel):
    years: int = Field(3, ge=1, le=10)
    granularity: Literal["monthly", "yearly"] = "monthly"
