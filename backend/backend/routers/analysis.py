from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlmodel import Session, select

from backend.core.database import get_db
from backend.models.overall import SalesData
from backend.models.origin import OriginShareData
from backend.schemas.analysis import (
    NevBreakdownDetailQuery,
    NevBreakdownQuery,
    NevShareOverviewQuery,
    NevShareTrendQuery,
    OriginShareOverviewQuery,
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
        yearly_rows = db.exec(select(
            SalesData.year,
            func.sum(SalesData.total_sales).label("total_sales"),
            func.sum(SalesData.nev_sales).label("nev_sales"),
        ).where(
            SalesData.year >= start_year,
            SalesData.data_type == "retail",
        ).group_by(SalesData.year).order_by(SalesData.year)).all()

        data = []
        for r in yearly_rows:
            total = float(r.total_sales or 0)
            nev = float(r.nev_sales or 0)
            rate = (nev / total * 100) if total else 0
            data.append({"year": r.year, "nev_penetration_rate": round(rate, 2), "total_sales": total, "nev_sales": nev})
    else:
        rows = db.exec(select(SalesData).where(
            SalesData.year >= start_year,
            SalesData.data_type == "retail",
        ).order_by(SalesData.year, SalesData.month)).all()

        data = []
        for r in rows:
            total = float(r.total_sales or 0)
            nev = float(r.nev_sales or 0)
            rate = (nev / total * 100) if total else 0
            data.append({
                "year": r.year, "month": r.month,
                "nev_penetration_rate": round(rate, 2),
                "total_sales": total, "nev_sales": nev,
            })

    return success(data)


@router.get("/nev-share/overview")
def nev_share_overview(
    query: NevShareOverviewQuery = Depends(),
    db: Session = Depends(get_db),
):
    row = db.exec(select(SalesData).where(
        SalesData.year == query.year,
        SalesData.month == query.month,
        SalesData.data_type == "retail",
    )).first()

    if not row:
        return success(None)

    total = float(row.total_sales) if row.total_sales else 0
    nev = float(row.nev_sales) if row.nev_sales else 0
    nev_penetration_rate = (nev / total * 100) if total else 0

    data = {
        "year": query.year,
        "month": query.month,
        "total_sales": total,
        "nev_sales": nev,
        "nev_penetration_rate": round(nev_penetration_rate, 2),
        "breakdown": [
            {"name": "纯电动", "value": float(row.bev_sales) if row.bev_sales else 0},
            {"name": "插电混动", "value": float(row.phev_sales) if row.phev_sales else 0},
            {"name": "其他混动", "value": float(row.hybrid_sales) if row.hybrid_sales else 0},
            {"name": "燃油车", "value": float(row.ice_sales) if row.ice_sales else 0},
        ],
    }

    return success(data)


@router.get("/nev-breakdown")
def nev_breakdown(
    query: NevBreakdownQuery = Depends(),
    db: Session = Depends(get_db),
):
    now = datetime.now()
    start_year = now.year - query.years + 1

    if query.granularity == "yearly":
        yearly_rows = db.exec(select(
            SalesData.year,
            func.sum(SalesData.nev_sales).label("nev_sales"),
            func.sum(SalesData.bev_sales).label("bev_sales"),
            func.sum(SalesData.phev_sales).label("phev_sales"),
            func.sum(SalesData.hybrid_sales).label("hybrid_sales"),
        ).where(
            SalesData.year >= start_year,
            SalesData.data_type == "retail",
        ).group_by(SalesData.year).order_by(SalesData.year)).all()

        data = []
        for r in yearly_rows:
            nev = float(r.nev_sales or 0)
            bev = float(r.bev_sales or 0)
            phev = float(r.phev_sales or 0)
            hybrid = float(r.hybrid_sales or 0)
            data.append({
                "year": r.year,
                "nev_sales": nev,
                "bev_sales": bev, "bev_ratio": round(bev / nev * 100, 2) if nev else 0,
                "phev_sales": phev, "phev_ratio": round(phev / nev * 100, 2) if nev else 0,
                "hybrid_sales": hybrid, "hybrid_ratio": round(hybrid / nev * 100, 2) if nev else 0,
            })
    else:
        rows = db.exec(select(SalesData).where(
            SalesData.year >= start_year,
            SalesData.data_type == "retail",
        ).order_by(SalesData.year, SalesData.month)).all()

        data = []
        for r in rows:
            nev = float(r.nev_sales or 0)
            bev = float(r.bev_sales or 0)
            phev = float(r.phev_sales or 0)
            hybrid = float(r.hybrid_sales or 0)
            data.append({
                "year": r.year, "month": r.month,
                "nev_sales": nev,
                "bev_sales": bev, "bev_ratio": round(bev / nev * 100, 2) if nev else 0,
                "phev_sales": phev, "phev_ratio": round(phev / nev * 100, 2) if nev else 0,
                "hybrid_sales": hybrid, "hybrid_ratio": round(hybrid / nev * 100, 2) if nev else 0,
            })

    return success(data)


@router.get("/nev-breakdown/detail")
def nev_breakdown_detail(
    query: NevBreakdownDetailQuery = Depends(),
    db: Session = Depends(get_db),
):
    row = db.exec(select(SalesData).where(
        SalesData.year == query.year,
        SalesData.month == query.month,
        SalesData.data_type == "retail",
    )).first()

    if not row:
        return success(None)

    nev = float(row.nev_sales) if row.nev_sales else 0
    bev = float(row.bev_sales) if row.bev_sales else 0
    phev = float(row.phev_sales) if row.phev_sales else 0
    hybrid = float(row.hybrid_sales) if row.hybrid_sales else 0

    return success({
        "year": query.year, "month": query.month,
        "nev_sales": nev,
        "bev_sales": bev, "bev_ratio": round(bev / nev * 100, 2) if nev else 0,
        "phev_sales": phev, "phev_ratio": round(phev / nev * 100, 2) if nev else 0,
        "hybrid_sales": hybrid, "hybrid_ratio": round(hybrid / nev * 100, 2) if nev else 0,
        "ice_sales": float(row.ice_sales) if row.ice_sales else 0,
    })


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
            for cn_key, en_key in ORIGIN_FIELD_MAP.items():
                sv = year_origins[year].get(cn_key, 0)
                entry[en_key] = round(sv / total * 100, 2) if total else 0
            data.append(entry)
    else:
        rows = db.exec(select(OriginShareData).where(
            OriginShareData.year >= start_year,
            OriginShareData.data_type == query.data_type,
        ).order_by(OriginShareData.year, OriginShareData.month)).all()

        month_totals: dict[tuple, float] = {}
        month_origins: dict[tuple, dict[str, float]] = {}
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
            entry = {"year": year, "month": month}
            total = month_totals[(year, month)]
            for cn_key, en_key in ORIGIN_FIELD_MAP.items():
                sv = month_origins[(year, month)].get(cn_key, 0)
                entry[en_key] = round(sv / total * 100, 2) if total else 0
            data.append(entry)

    return success(data)


@router.get("/origin-share/overview")
def origin_share_overview(
    query: OriginShareOverviewQuery = Depends(),
    db: Session = Depends(get_db),
):
    rows = db.exec(select(OriginShareData).where(
        OriginShareData.year == query.year,
        OriginShareData.month == query.month,
        OriginShareData.data_type == query.data_type,
    )).all()

    if not rows:
        return success(None)

    total = sum(float(r.sales_volume or 0) for r in rows)
    result: dict = {"year": query.year, "month": query.month}
    for r in rows:
        field = ORIGIN_FIELD_MAP.get(r.origin, "other")
        sv = float(r.sales_volume or 0)
        result[field] = round(sv / total * 100, 2) if total else 0

    return success(result)
