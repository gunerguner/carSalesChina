from dataclasses import dataclass
from typing import Any

from backend.common.types import AnalysisPeriodRow, Granularity, LevelType


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


LevelSalesByPeriod = dict[PeriodKey, dict[LevelType, float]]


def period_entry(key: PeriodKey) -> AnalysisPeriodRow:
    if key.month is None:
        return {"year": key.year}
    return {"year": key.year, "month": key.month}
