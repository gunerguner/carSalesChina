from collections import defaultdict
from datetime import datetime
from importlib.resources import files

import yaml
from sqlalchemy import func
from sqlmodel import Session, select

from backend.common.periods import (
    LevelSalesByPeriod,
    PeriodKey,
    period_columns,
    period_entry,
    period_key,
)
from backend.common.types import (
    Granularity,
    NevBreakdownRow,
    NevShareTrendRow,
    OriginShareTrendRow,
)
from backend.core.exceptions import AppError, ValidationAppError
from backend.models.origin import OriginShareData
from backend.models.overall import SalesData

_ORIGIN_FIELD_MAP_PATH = files("backend") / "origin_field_map.yaml"


def _load_origin_field_map() -> dict[str, str]:
    with open(_ORIGIN_FIELD_MAP_PATH, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    if not isinstance(raw, dict):
        return {}
    return {str(k): str(v) for k, v in raw.items()}


ORIGIN_FIELD_MAP = _load_origin_field_map()


def _start_year(years: int) -> int:
    if years <= 0:
        raise ValidationAppError("years 必须大于 0")
    return datetime.now().year - years + 1


def _percent(part: float, total: float) -> float:
    return round(part / total * 100, 2) if total else 0


def _sales_by_period_and_level(
    db: Session,
    *,
    start_year: int,
    levels: tuple[str, ...],
    granularity: Granularity,
) -> LevelSalesByPeriod:
    period_cols = period_columns(SalesData, granularity)
    rows = db.exec(
        select(
            *period_cols,
            SalesData.level_type,
            func.sum(SalesData.sales).label("sales"),
        )
        .where(
            SalesData.year >= start_year,
            SalesData.data_type == "retail",
            SalesData.date_type == "monthly",
            SalesData.level_type.in_(list(levels)),
        )
        .group_by(*period_cols, SalesData.level_type)
        .order_by(*period_cols)
    ).all()

    grouped: LevelSalesByPeriod = defaultdict(dict)
    for row in rows:
        grouped[period_key(row, granularity)][row.level_type] = float(row.sales or 0)
    return dict(grouped)


def _nev_share_row(key: PeriodKey, levels: dict[str, float]) -> NevShareTrendRow:
    total = levels.get("all", 0)
    nev = levels.get("nev", 0)
    return {
        **period_entry(key),
        "nev_penetration_rate": _percent(nev, total),
        "total_sales": total,
        "nev_sales": nev,
    }


def _nev_breakdown_row(key: PeriodKey, levels: dict[str, float]) -> NevBreakdownRow:
    nev = levels.get("nev", 0)
    bev = levels.get("bev", 0)
    phev = max(nev - bev, 0)
    return {
        **period_entry(key),
        "nev_sales": nev,
        "bev_sales": bev,
        "bev_ratio": _percent(bev, nev),
        "phev_sales": phev,
        "phev_ratio": _percent(phev, nev),
        "hybrid_sales": 0,
        "hybrid_ratio": 0,
    }


def _origin_share_row(
    key: PeriodKey,
    origins: dict[str, float],
    total: float,
) -> OriginShareTrendRow:
    return {
        **period_entry(key),
        **{
            origin_en: _percent(origins.get(origin_cn, 0), total)
            for origin_cn, origin_en in ORIGIN_FIELD_MAP.items()
        },
    }


def get_nev_share_trend(
    db: Session, years: int, granularity: Granularity
) -> list[NevShareTrendRow]:
    period_data = _sales_by_period_and_level(
        db,
        start_year=_start_year(years),
        levels=("all", "nev"),
        granularity=granularity,
    )
    return [_nev_share_row(key, period_data[key]) for key in sorted(period_data)]


def get_nev_breakdown(
    db: Session, years: int, granularity: Granularity
) -> list[NevBreakdownRow]:
    """同期纯电占新能源比例：bev / nev；nev、bev 为易车口径下的新能源、纯电级别销量。"""
    period_data = _sales_by_period_and_level(
        db,
        start_year=_start_year(years),
        levels=("nev", "bev"),
        granularity=granularity,
    )
    return [_nev_breakdown_row(key, period_data[key]) for key in sorted(period_data)]


def get_origin_share_trend(
    db: Session,
    years: int,
    granularity: Granularity,
) -> list[OriginShareTrendRow]:
    if not ORIGIN_FIELD_MAP:
        raise AppError(message="origin_field_map 配置为空或格式错误")

    period_cols = period_columns(OriginShareData, granularity)
    rows = db.exec(
        select(
            *period_cols,
            OriginShareData.origin,
            func.sum(OriginShareData.sales_volume).label("sales_volume"),
        )
        .where(
            OriginShareData.year >= _start_year(years),
        )
        .group_by(*period_cols, OriginShareData.origin)
        .order_by(*period_cols)
    ).all()

    period_totals: dict[PeriodKey, float] = defaultdict(float)
    period_origins: dict[PeriodKey, dict[str, float]] = defaultdict(dict)
    for row in rows:
        key = period_key(row, granularity)
        sales = float(row.sales_volume or 0)
        period_totals[key] += sales
        period_origins[key][row.origin] = sales

    return [
        _origin_share_row(key, period_origins[key], period_totals[key])
        for key in sorted(period_origins)
    ]
