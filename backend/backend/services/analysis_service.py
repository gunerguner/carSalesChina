from datetime import datetime
from importlib.resources import files
from typing import Any, Iterable

import yaml
from sqlalchemy import func
from sqlmodel import Session, select

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
    return datetime.now().year - years + 1


def _percent(part: float, total: float) -> float:
    return round(part / total * 100, 2) if total else 0


def _period_columns(granularity: str):
    return (
        (SalesData.year,)
        if granularity == "yearly"
        else (SalesData.year, SalesData.month)
    )


def _origin_period_columns(granularity: str):
    return (
        (OriginShareData.year,)
        if granularity == "yearly"
        else (OriginShareData.year, OriginShareData.month)
    )


def _period_key(row: Any, granularity: str) -> int | tuple[int, int]:
    return row.year if granularity == "yearly" else (row.year, row.month)


def _period_entry(key: int | tuple[int, int]) -> dict[str, int]:
    if isinstance(key, tuple):
        year, month = key
        return {"year": year, "month": month}
    return {"year": key}


def _sales_by_period_and_level(
    db: Session,
    *,
    start_year: int,
    levels: Iterable[str],
    granularity: str,
) -> dict[int | tuple[int, int], dict[str, float]]:
    period_cols = _period_columns(granularity)
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

    grouped: dict[int | tuple[int, int], dict[str, float]] = {}
    for row in rows:
        grouped.setdefault(_period_key(row, granularity), {})[row.level_type] = float(
            row.sales or 0
        )
    return grouped


def get_nev_share_trend(
    db: Session, years: int, granularity: str
) -> list[dict[str, Any]]:
    period_data = _sales_by_period_and_level(
        db,
        start_year=_start_year(years),
        levels=("all", "nev"),
        granularity=granularity,
    )

    data: list[dict[str, Any]] = []
    for key in sorted(period_data):
        levels = period_data[key]
        total = levels.get("all", 0)
        nev = levels.get("nev", 0)
        data.append(
            {
                **_period_entry(key),
                "nev_penetration_rate": _percent(nev, total),
                "total_sales": total,
                "nev_sales": nev,
            }
        )
    return data


def get_nev_breakdown(
    db: Session, years: int, granularity: str
) -> list[dict[str, Any]]:
    period_data = _sales_by_period_and_level(
        db,
        start_year=_start_year(years),
        levels=("nev", "bev"),
        granularity=granularity,
    )

    data: list[dict[str, Any]] = []
    for key in sorted(period_data):
        levels = period_data[key]
        nev = levels.get("nev", 0)
        bev = levels.get("bev", 0)
        phev = max(nev - bev, 0)
        data.append(
            {
                **_period_entry(key),
                "nev_sales": nev,
                "bev_sales": bev,
                "bev_ratio": _percent(bev, nev),
                "phev_sales": phev,
                "phev_ratio": _percent(phev, nev),
                "hybrid_sales": 0,
                "hybrid_ratio": 0,
            }
        )
    return data


def get_origin_share_trend(
    db: Session,
    years: int,
    granularity: str,
) -> list[dict[str, Any]]:
    period_cols = _origin_period_columns(granularity)
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

    period_totals: dict[int | tuple[int, int], float] = {}
    period_origins: dict[int | tuple[int, int], dict[str, float]] = {}
    for row in rows:
        key = _period_key(row, granularity)
        sales = float(row.sales_volume or 0)
        period_totals[key] = period_totals.get(key, 0) + sales
        period_origins.setdefault(key, {})[row.origin] = sales

    data: list[dict[str, Any]] = []
    for key in sorted(period_origins):
        total = period_totals[key]
        entry: dict[str, Any] = _period_entry(key)
        origins = period_origins[key]
        for origin_cn, origin_en in ORIGIN_FIELD_MAP.items():
            entry[origin_en] = _percent(origins.get(origin_cn, 0), total)
        data.append(entry)
    return data
