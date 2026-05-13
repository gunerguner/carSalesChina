from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy import func
from sqlmodel import Session, select

from backend.models.origin import OriginShareData
from backend.models.overall import SalesData

_ORIGIN_FIELD_MAP_PATH = Path(__file__).resolve().parent.parent / "origin_field_map.yaml"


def _load_origin_field_map() -> dict[str, str]:
    with open(_ORIGIN_FIELD_MAP_PATH, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    if not isinstance(raw, dict):
        return {}
    return {str(k): str(v) for k, v in raw.items()}


ORIGIN_FIELD_MAP = _load_origin_field_map()


def get_nev_share_trend(db: Session, years: int, granularity: str) -> list[dict[str, Any]]:
    now = datetime.now()
    start_year = now.year - years + 1

    if granularity == "yearly":
        yearly_rows = db.exec(
            select(
                SalesData.year,
                SalesData.level_type,
                func.sum(SalesData.sales).label("sales"),
            )
            .where(
                SalesData.year >= start_year,
                SalesData.data_type == "retail",
                SalesData.date_type == "monthly",
                SalesData.level_type.in_(["all", "nev"]),
            )
            .group_by(SalesData.year, SalesData.level_type)
            .order_by(SalesData.year)
        ).all()

        year_data: dict[int, dict[str, float]] = {}
        for row in yearly_rows:
            if row.year not in year_data:
                year_data[row.year] = {}
            year_data[row.year][row.level_type] = float(row.sales or 0)

        data: list[dict[str, Any]] = []
        for year in sorted(year_data.keys()):
            total = year_data[year].get("all", 0)
            nev = year_data[year].get("nev", 0)
            rate = (nev / total * 100) if total else 0
            data.append(
                {
                    "year": year,
                    "nev_penetration_rate": round(rate, 2),
                    "total_sales": total,
                    "nev_sales": nev,
                }
            )
        return data

    rows = db.exec(
        select(SalesData)
        .where(
            SalesData.year >= start_year,
            SalesData.data_type == "retail",
            SalesData.date_type == "monthly",
            SalesData.level_type.in_(["all", "nev"]),
        )
        .order_by(SalesData.year, SalesData.month)
    ).all()

    month_data: dict[tuple[int, int], dict[str, float]] = {}
    for row in rows:
        key = (row.year, row.month)
        if key not in month_data:
            month_data[key] = {}
        month_data[key][row.level_type] = float(row.sales or 0)

    data: list[dict[str, Any]] = []
    for (year, month), levels in sorted(month_data.items()):
        total = levels.get("all", 0)
        nev = levels.get("nev", 0)
        rate = (nev / total * 100) if total else 0
        data.append(
            {
                "year": year,
                "month": month,
                "nev_penetration_rate": round(rate, 2),
                "total_sales": total,
                "nev_sales": nev,
            }
        )
    return data


def get_nev_breakdown(db: Session, years: int, granularity: str) -> list[dict[str, Any]]:
    now = datetime.now()
    start_year = now.year - years + 1

    if granularity == "yearly":
        yearly_rows = db.exec(
            select(
                SalesData.year,
                SalesData.level_type,
                func.sum(SalesData.sales).label("sales"),
            )
            .where(
                SalesData.year >= start_year,
                SalesData.data_type == "retail",
                SalesData.date_type == "monthly",
                SalesData.level_type.in_(["nev", "bev"]),
            )
            .group_by(SalesData.year, SalesData.level_type)
            .order_by(SalesData.year)
        ).all()

        year_data: dict[int, dict[str, float]] = {}
        for row in yearly_rows:
            if row.year not in year_data:
                year_data[row.year] = {}
            year_data[row.year][row.level_type] = float(row.sales or 0)

        data: list[dict[str, Any]] = []
        for year in sorted(year_data.keys()):
            nev = year_data[year].get("nev", 0)
            bev = year_data[year].get("bev", 0)
            other_nev = max(nev - bev, 0)
            data.append(
                {
                    "year": year,
                    "nev_sales": nev,
                    "bev_sales": bev,
                    "bev_ratio": round(bev / nev * 100, 2) if nev else 0,
                    "phev_sales": other_nev,
                    "phev_ratio": round(other_nev / nev * 100, 2) if nev else 0,
                    "hybrid_sales": 0,
                    "hybrid_ratio": 0,
                }
            )
        return data

    rows = db.exec(
        select(SalesData)
        .where(
            SalesData.year >= start_year,
            SalesData.data_type == "retail",
            SalesData.date_type == "monthly",
            SalesData.level_type.in_(["nev", "bev"]),
        )
        .order_by(SalesData.year, SalesData.month)
    ).all()

    month_data: dict[tuple[int, int], dict[str, float]] = {}
    for row in rows:
        key = (row.year, row.month)
        if key not in month_data:
            month_data[key] = {}
        month_data[key][row.level_type] = float(row.sales or 0)

    data: list[dict[str, Any]] = []
    for (year, month), levels in sorted(month_data.items()):
        nev = levels.get("nev", 0)
        bev = levels.get("bev", 0)
        other_nev = max(nev - bev, 0)
        data.append(
            {
                "year": year,
                "month": month,
                "nev_sales": nev,
                "bev_sales": bev,
                "bev_ratio": round(bev / nev * 100, 2) if nev else 0,
                "phev_sales": other_nev,
                "phev_ratio": round(other_nev / nev * 100, 2) if nev else 0,
                "hybrid_sales": 0,
                "hybrid_ratio": 0,
            }
        )
    return data


def get_origin_share_trend(
    db: Session,
    years: int,
    granularity: str,
    data_type: str,
) -> list[dict[str, Any]]:
    now = datetime.now()
    start_year = now.year - years + 1

    if granularity == "yearly":
        rows = db.exec(
            select(
                OriginShareData.year,
                OriginShareData.origin,
                func.sum(OriginShareData.sales_volume).label("sales_volume"),
            )
            .where(
                OriginShareData.year >= start_year,
                OriginShareData.data_type == data_type,
            )
            .group_by(OriginShareData.year, OriginShareData.origin)
        ).all()

        year_totals: dict[int, float] = {}
        year_origins: dict[int, dict[str, float]] = {}
        for row in rows:
            if row.year not in year_origins:
                year_origins[row.year] = {}
                year_totals[row.year] = 0
            sv = float(row.sales_volume or 0)
            year_origins[row.year][row.origin] = sv
            year_totals[row.year] += sv

        data: list[dict[str, Any]] = []
        for year in sorted(year_origins.keys()):
            entry: dict[str, Any] = {"year": year}
            total = year_totals[year]
            for origin_cn, origin_en in ORIGIN_FIELD_MAP.items():
                sv = year_origins[year].get(origin_cn, 0)
                entry[origin_en] = round(sv / total * 100, 2) if total else 0
            data.append(entry)
        return data

    rows = db.exec(
        select(OriginShareData)
        .where(
            OriginShareData.year >= start_year,
            OriginShareData.data_type == data_type,
        )
        .order_by(OriginShareData.year, OriginShareData.month)
    ).all()

    month_totals: dict[tuple[int, int], float] = {}
    month_origins: dict[tuple[int, int], dict[str, float]] = {}
    for row in rows:
        key = (row.year, row.month)
        if key not in month_origins:
            month_origins[key] = {}
            month_totals[key] = 0
        sv = float(row.sales_volume or 0)
        month_origins[key][row.origin] = sv
        month_totals[key] += sv

    data: list[dict[str, Any]] = []
    for (year, month) in sorted(month_origins.keys()):
        entry: dict[str, Any] = {"year": year, "month": month}
        total = month_totals[(year, month)]
        for origin_cn, origin_en in ORIGIN_FIELD_MAP.items():
            sv = month_origins[(year, month)].get(origin_cn, 0)
            entry[origin_en] = round(sv / total * 100, 2) if total else 0
        data.append(entry)
    return data
