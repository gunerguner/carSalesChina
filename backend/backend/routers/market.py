from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.core.database import get_db
from backend.models.overall import SalesData
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
    year: int = Query(...),
    month: int = Query(...),
    energy_type: str = Query("all"),
    data_type: str = DATA_TYPE_ENUM,
    db: Session = Depends(get_db),
):
    row = db.query(SalesData).filter(
        SalesData.year == year,
        SalesData.month == month,
        SalesData.data_type == data_type,
    ).first()
    if not row:
        return success(None)

    prev_month_row = db.query(SalesData).filter(
        SalesData.year == (year if month > 1 else year - 1),
        SalesData.month == (month - 1 if month > 1 else 12),
        SalesData.data_type == data_type,
    ).first()

    prev_year_row = db.query(SalesData).filter(
        SalesData.year == year - 1,
        SalesData.month == month,
        SalesData.data_type == data_type,
    ).first()

    field = ENERGY_FIELD_MAP.get(energy_type, "total_sales")
    current_val = getattr(row, field) or 0
    prev_month_val = getattr(prev_month_row, field) or 0 if prev_month_row else 0
    prev_year_val = getattr(prev_year_row, field) or 0 if prev_year_row else 0

    mom_growth = ((current_val - prev_month_val) / prev_month_val * 100) if prev_month_val else None
    yoy_growth = ((current_val - prev_year_val) / prev_year_val * 100) if prev_year_val else None

    total_sales = float(row.total_sales) if row.total_sales else 0
    nev_sales = float(row.nev_sales) if row.nev_sales else 0
    nev_penetration_rate = (nev_sales / total_sales * 100) if total_sales else 0

    return success({
        "year": year,
        "month": month,
        "energy_type": energy_type,
        "data_type": data_type,
        "sales": float(current_val),
        "mom_growth": round(mom_growth, 2) if mom_growth else None,
        "yoy_growth": round(yoy_growth, 2) if yoy_growth else None,
        "total_sales": total_sales,
        "nev_sales": nev_sales,
        "ice_sales": float(row.ice_sales) if row.ice_sales else 0,
        "bev_sales": float(row.bev_sales) if row.bev_sales else 0,
        "phev_sales": float(row.phev_sales) if row.phev_sales else 0,
        "hybrid_sales": float(row.hybrid_sales) if row.hybrid_sales else 0,
        "nev_penetration_rate": round(nev_penetration_rate, 2),
    })


@router.get("/trend")
def trend(
    energy_type: str = Query("all"),
    years: int = Query(3),
    granularity: str = Query("monthly"),
    data_type: str = DATA_TYPE_ENUM,
    db: Session = Depends(get_db),
):
    now = datetime.now()
    start_year = now.year - years + 1

    field = ENERGY_FIELD_MAP.get(energy_type, "total_sales")

    if granularity == "yearly":
        rows = db.query(
            SalesData.year,
            func.sum(getattr(SalesData, field)).label("sales"),
        ).filter(
            SalesData.year >= start_year,
            SalesData.data_type == data_type,
        ).group_by(SalesData.year).order_by(SalesData.year).all()

        data = [{"year": r.year, "sales": float(r.sales or 0)} for r in rows]
    else:
        rows = db.query(SalesData).filter(
            SalesData.year >= start_year,
            SalesData.data_type == data_type,
        ).order_by(SalesData.year, SalesData.month).all()

        data = []
        for r in rows:
            data.append({
                "year": r.year,
                "month": r.month,
                "sales": float(getattr(r, field) or 0),
            })

    return success(data)


@router.get("/compare")
def compare(
    energy_type: str = Query("all"),
    start_year: int = Query(...),
    start_month: int = Query(...),
    end_year: int = Query(...),
    end_month: int = Query(...),
    data_type: str = DATA_TYPE_ENUM,
    db: Session = Depends(get_db),
):
    field = ENERGY_FIELD_MAP.get(energy_type, "total_sales")

    rows = db.query(SalesData).filter(
        SalesData.data_type == data_type,
    ).order_by(SalesData.year, SalesData.month).all()

    period1 = []
    period2 = []
    for r in rows:
        val = float(getattr(r, field) or 0)
        entry = {"year": r.year, "month": r.month, "sales": val}

        if (r.year, r.month) >= (start_year, start_month) and (r.year, r.month) <= (end_year, end_month):
            period2.append(entry)

    if period2:
        start = (start_year, start_month)
        months_diff = (end_year - start_year) * 12 + end_month - start_month + 1
        p1_start_year = start_year - (months_diff // 12 + 1)
        p1_start_month = start_month - (months_diff % 12)
        if p1_start_month <= 0:
            p1_start_month += 12
            p1_start_year -= 1
        p1_end_year = start_year - 1 if start_month == 1 else start_year
        p1_end_month = start_month - 1 if start_month > 1 else 12

        for r in rows:
            val = float(getattr(r, field) or 0)
            entry = {"year": r.year, "month": r.month, "sales": val}
            if (r.year, r.month) >= (p1_start_year, p1_start_month) and (r.year, r.month) <= (p1_end_year, p1_end_month):
                period1.append(entry)

    sum1 = sum(e["sales"] for e in period1)
    sum2 = sum(e["sales"] for e in period2)
    change = ((sum2 - sum1) / sum1 * 100) if sum1 else None

    return success({
        "period1": {"data": period1, "total": sum1},
        "period2": {"data": period2, "total": sum2},
        "change_pct": round(change, 2) if change else None,
    })


@router.get("/yearly")
def yearly(
    year: int = Query(...),
    energy_type: str = Query("all"),
    data_type: str = DATA_TYPE_ENUM,
    db: Session = Depends(get_db),
):
    min_year = db.query(func.min(SalesData.year)).filter(
        SalesData.data_type == data_type,
    ).scalar() or year - 2

    field = ENERGY_FIELD_MAP.get(energy_type, "total_sales")
    rows = db.query(SalesData).filter(
        SalesData.year >= min_year,
        SalesData.data_type == data_type,
    ).order_by(SalesData.year, SalesData.month).all()

    all_rows_map = {(r.year, r.month): r for r in rows}
    years_in_data = sorted(set(r.year for r in rows))

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


@router.get("/byEnergyType")
def by_energy_type(
    year: int = Query(...),
    month: int = Query(...),
    data_type: str = DATA_TYPE_ENUM,
    db: Session = Depends(get_db),
):
    row = db.query(SalesData).filter(
        SalesData.year == year,
        SalesData.month == month,
        SalesData.data_type == data_type,
    ).first()
    if not row:
        return success([])

    total = float(row.total_sales) if row.total_sales else 0
    data = [
        {"name": "纯电动", "value": float(row.bev_sales) if row.bev_sales else 0},
        {"name": "插电混动", "value": float(row.phev_sales) if row.phev_sales else 0},
        {"name": "其他混动", "value": float(row.hybrid_sales) if row.hybrid_sales else 0},
        {"name": "燃油车", "value": float(row.ice_sales) if row.ice_sales else 0},
    ]
    if total:
        for item in data:
            item["percent"] = round(item["value"] / total * 100, 2)

    return success(data)