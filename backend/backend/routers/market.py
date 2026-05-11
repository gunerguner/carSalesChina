from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlmodel import Session, select

from backend.core.database import get_db
from backend.models.overall import SalesData
from backend.schemas.market import OverviewQuery, TrendQuery, YearlyQuery
from backend.schemas.response import success

router = APIRouter(prefix="/api/v1/market", tags=["market"])

ENERGY_FIELD_MAP = {
    "all": "total_sales",
    "fuel": "ice_sales",
    "bev": "bev_sales",
    "phev": "phev_sales",
    "hybrid": "hybrid_sales",
}

DATA_TYPE_ENUM = Query("retail", pattern="^(retail|wholesale|production)$")


@router.get("/overview")
def overview(
    query: OverviewQuery = Depends(),
    db: Session = Depends(get_db),
):
    row = db.exec(select(SalesData).where(
        SalesData.year == query.year,
        SalesData.month == query.month,
        SalesData.data_type == query.data_type,
    )).first()

    prev_month_row = db.exec(select(SalesData).where(
        SalesData.year == (query.year if query.month > 1 else query.year - 1),
        SalesData.month == (query.month - 1 if query.month > 1 else 12),
        SalesData.data_type == query.data_type,
    )).first()

    prev_year_row = db.exec(select(SalesData).where(
        SalesData.year == query.year - 1,
        SalesData.month == query.month,
        SalesData.data_type == query.data_type,
    )).first()

    field = ENERGY_FIELD_MAP.get(query.energy_type, "total_sales")
    current_val = getattr(row, field) or 0 if row else 0
    prev_month_val = getattr(prev_month_row, field) or 0 if prev_month_row else 0
    prev_year_val = getattr(prev_year_row, field) or 0 if prev_year_row else 0

    mom_growth = ((current_val - prev_month_val) / prev_month_val * 100) if prev_month_val else None
    yoy_growth = ((current_val - prev_year_val) / prev_year_val * 100) if prev_year_val else None

    total_sales = float(row.total_sales) if row and row.total_sales else 0
    nev_sales = float(row.nev_sales) if row and row.nev_sales else 0
    nev_penetration_rate = (nev_sales / total_sales * 100) if total_sales else 0

    return success({
        "year": query.year,
        "month": query.month,
        "energy_type": query.energy_type,
        "data_type": query.data_type,
        "sales": float(current_val),
        "mom_growth": round(mom_growth, 2) if mom_growth else None,
        "yoy_growth": round(yoy_growth, 2) if yoy_growth else None,
        "total_sales": total_sales,
        "nev_sales": nev_sales,
        "ice_sales": float(row.ice_sales) if row and row.ice_sales else 0,
        "bev_sales": float(row.bev_sales) if row and row.bev_sales else 0,
        "phev_sales": float(row.phev_sales) if row and row.phev_sales else 0,
        "hybrid_sales": float(row.hybrid_sales) if row and row.hybrid_sales else 0,
        "nev_penetration_rate": round(nev_penetration_rate, 2),
    })


@router.get("/trend")
def trend(
    query: TrendQuery = Depends(),
    db: Session = Depends(get_db),
):
    now = datetime.now()
    start_year = now.year - query.years + 1
    field = ENERGY_FIELD_MAP.get(query.energy_type, "total_sales")

    if query.granularity == "yearly":
        rows = db.exec(select(
            SalesData.year,
            func.sum(getattr(SalesData, field)).label("sales"),
        ).where(
            SalesData.year >= start_year,
            SalesData.data_type == query.data_type,
        ).group_by(SalesData.year).order_by(SalesData.year)).all()

        data = [{"year": r.year, "sales": float(r.sales or 0)} for r in rows]
    else:
        rows = db.exec(select(SalesData).where(
            SalesData.year >= start_year,
            SalesData.data_type == query.data_type,
        ).order_by(SalesData.year, SalesData.month)).all()

        data = [{"year": r.year, "month": r.month, "sales": float(getattr(r, field) or 0)} for r in rows]

    return success(data)





@router.get("/yearly")
def yearly(
    query: YearlyQuery = Depends(),
    db: Session = Depends(get_db),
):
    min_year = db.execute(select(func.min(SalesData.year)).where(
        SalesData.data_type == query.data_type,
    )).scalar() or query.year - 2

    field = ENERGY_FIELD_MAP.get(query.energy_type, "total_sales")
    rows = db.exec(select(SalesData).where(
        SalesData.year >= min_year,
        SalesData.data_type == query.data_type,
    ).order_by(SalesData.year, SalesData.month)).all()

    all_rows_map = {(r.year, r.month): r for r in rows}

    data = []
    for r in rows:
        prev_month_key = (r.year - 1, 12) if r.month == 1 else (r.year, r.month - 1)
        prev_year_key = (r.year - 1, r.month)

        prev_month_row = all_rows_map.get(prev_month_key)
        prev_year_row = all_rows_map.get(prev_year_key)

        current_val = float(getattr(r, field) or 0)
        prev_month_val = float(getattr(prev_month_row, field) or 0) if prev_month_row else 0
        prev_year_val = float(getattr(prev_year_row, field) or 0) if prev_year_row else 0

        mom_growth = ((current_val - prev_month_val) / prev_month_val * 100) if prev_month_val else None
        yoy_growth = ((current_val - prev_year_val) / prev_year_val * 100) if prev_year_val else None

        data.append({
            "year": r.year,
            "month": r.month,
            "sales": current_val,
            "yoy_growth": round(yoy_growth, 2) if yoy_growth else None,
            "mom_growth": round(mom_growth, 2) if mom_growth else None,
            "total_sales": float(r.total_sales) if r.total_sales else 0,
            "nev_sales": float(r.nev_sales) if r.nev_sales else 0,
            "ice_sales": float(r.ice_sales) if r.ice_sales else 0,
        })

    return success(data)



