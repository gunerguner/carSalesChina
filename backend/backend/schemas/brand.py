from typing import Literal

from pydantic import BaseModel, Field, field_validator


class TrendAllPeriodsQuery(BaseModel):
    brand_names: list[str] = Field(...)
    data_type: Literal["retail", "production"] = "retail"

    @field_validator("brand_names", mode="before")
    @classmethod
    def split_brand_names(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            parts = value
        else:
            parts = ",".join(str(item) for item in value)
        names = [name.strip() for name in parts.split(",") if name.strip()][:3]
        if not names:
            raise ValueError("brand_names 不能为空")
        return names
