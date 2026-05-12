from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlmodel import Session, select

from backend.core.database import get_db
from backend.models.overall import SalesData
from backend.models.origin import OriginShareData
from backend.schemas.analysis import (
    NevBreakdownQuery,
    NevShareTrendQuery,
    OriginShareTrendQuery,
)
from backend.schemas.response import success

router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])

ORIGIN_FIELD_MAP = {
    "自主": "domestic",
    "德系": "german",
    "日系": "japanese",
    "美系": "american",
    "其他欧系": "european",
    "法系": "french",
    "韩系": "korean",
}


@router.get("/nev-share/trend")
def nev_share_trend(
    query: NevShareTrendQuery = Depends(),
    db: Session = Depends(get_db),
):
    now = datetime.now()
    start_year = now.year - query.years + 1

    if query.granularity == "yearly":
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
        for r in yearly_rows:
            if r.year not in year_data:
                year_data[r.year] = {}
            year_data[r.year][r.level_type] = float(r.sales or 0)

        data = []
        for year in sorted(year_data.keys()):
            total = year_data[year].get("all", 0)
            nev = year_data[year].get("nev", 0)
            rate = (nev / total * 100) if total else 0
            data.append({
                "year": year,
                "nev_penetration_rate": round(rate, 2),
                "total_sales": total,
                "nev_sales": nev,
            })
    else:
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
        for r in rows:
            key = (r.year, r.month)
            if key not in month_data:
                month_data[key] = {}
            month_data[key][r.level_type] = float(r.sales or 0)

        data = []
        for (year, month), levels in sorted(month_data.items()):
            total = levels.get("all", 0)
            nev = levels.get("nev", 0)
            rate = (nev / total * 100) if total else 0
            data.append({
                "year": year,
                "month": month,
                "nev_penetration_rate": round(rate, 2),
                "total_sales": total,
                "nev_sales": nev,
            })

    return success(data)


@router.get("/nev-breakdown")
def nev_breakdown(
    query: NevBreakdownQuery = Depends(),
    db: Session = Depends(get_db),
):
    now = datetime.now()
    start_year = now.year - query.years + 1

    if query.granularity == "yearly":
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
        for r in yearly_rows:
            if r.year not in year_data:
                year_data[r.year] = {}
            year_data[r.year][r.level_type] = float(r.sales or 0)

        data = []
        for year in sorted(year_data.keys()):
            nev = year_data[year].get("nev", 0)
            bev = year_data[year].get("bev", 0)
            other_nev = max(nev - bev, 0)
            data.append({
                "year": year,
                "nev_sales": nev,
                "bev_sales": bev,
                "bev_ratio": round(bev / nev * 100, 2) if nev else 0,
                "phev_sales": other_nev,
                "phev_ratio": round(other_nev / nev * 100, 2) if nev else 0,
                "hybrid_sales": 0,
                "hybrid_ratio": 0,
            })
    else:
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
        for r in rows:
            key = (r.year, r.month)
            if key not in month_data:
                month_data[key] = {}
            month_data[key][r.level_type] = float(r.sales or 0)

        data = []
        for (year, month), levels in sorted(month_data.items()):
            nev = levels.get("nev", 0)
            bev = levels.get("bev", 0)
            other_nev = max(nev - bev, 0)
            data.append({
                "year": year,
                "month": month,
                "nev_sales": nev,
                "bev_sales": bev,
                "bev_ratio": round(bev / nev * 100, 2) if nev else 0,
                "phev_sales": other_nev,
                "phev_ratio": round(other_nev / nev * 100, 2) if nev else 0,
                "hybrid_sales": 0,
                "hybrid_ratio": 0,
            })

    return success(data)


@router.get("/origin-share/trend")
def origin_share_trend(
    query: OriginShareTrendQuery = Depends(),
    db: Session = Depends(get_db),
):
    now = datetime.now()
    start_year = now.year - query.years + 1

    if query.granularity == "yearly":
        rows = db.exec(select(
            OriginShareData.year,
            OriginShareData.origin,
            func.sum(OriginShareData.sales_volume).label("sales_volume"),
        ).where(
            OriginShareData.year >= start_year,
            OriginShareData.data_type == query.data_type,
        ).group_by(OriginShareData.year, OriginShareData.origin)).all()

        year_totals: dict[int, float] = {}
        year_origins: dict[int, dict[str, float]] = {}
        for r in rows:
            if r.year not in year_origins:
                year_origins[r.year] = {}
                year_totals[r.year] = 0
            sv = float(r.sales_volume or 0)
            year_origins[r.year][r.origin] = sv
            year_totals[r.year] += sv

        data = []
        for year in sorted(year_origins.keys()):
            entry: dict = {"year": year}
            total = year_totals[year]
            for origin_cn, origin_en in ORIGIN_FIELD_MAP.items():
                sv = year_origins[year].get(origin_cn, 0)
                entry[origin_en] = round(sv / total * 100, 2) if total else 0
            data.append(entry)
    else:
        rows = db.exec(select(OriginShareData).where(
            OriginShareData.year >= start_year,
            OriginShareData.data_type == query.data_type,
        ).order_by(OriginShareData.year, OriginShareData.month)).all()

        month_totals: dict[tuple[int, int], float] = {}
        month_origins: dict[tuple[int, int], dict[str, float]] = {}
        for r in rows:
            key = (r.year, r.month)
            if key not in month_origins:
                month_origins[key] = {}
                month_totals[key] = 0
            sv = float(r.sales_volume or 0)
            month_origins[key][r.origin] = sv
            month_totals[key] += sv

        data = []
        for (year, month) in sorted(month_origins.keys()):
            entry: dict = {"year": year, "month": month}
            total = month_totals[(year, month)]
            for origin_cn, origin_en in ORIGIN_FIELD_MAP.items():
                sv = month_origins[(year, month)].get(origin_cn, 0)
                entry[origin_en] = round(sv / total * 100, 2) if total else 0
            data.append(entry)

    return success(data)