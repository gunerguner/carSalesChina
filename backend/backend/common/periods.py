from dataclasses import dataclass
from typing import Any, Literal

Granularity = Literal["monthly", "yearly"]


@dataclass(frozen=True, slots=True, order=True)
class PeriodKey:
    year: int
    month: int | None = None


def period_columns(model_cls: type, granularity: Granularity) -> tuple:
    if granularity == "yearly":
        return (model_cls.year,)
    return (model_cls.year, model_cls.month)


def period_key(row: Any, granularity: Granularity) -> PeriodKey:
    month = None if granularity == "yearly" else row.month
    return PeriodKey(row.year, month)


def period_entry(key: PeriodKey) -> dict[str, int]:
    if key.month is None:
        return {"year": key.year}
    return {"year": key.year, "month": key.month}
