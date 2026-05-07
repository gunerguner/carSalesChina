from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.src.core.database import get_db
from backend.src.models.overall import MonthlyOverall
from backend.src.schemas.response import success

router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])


@router.get("/nev-share/trend")
def nev_share_trend(
    years: int = Query(3),
    granularity: str = Query("monthly"),
    db: Session = Depends(get_db),
):
    now = datetime.now()
    start_year = now.year - years + 1

    rows = db.query(MonthlyOverall).filter(
        MonthlyOverall.year >= start_year,
        MonthlyOverall.data_type == "retail",
    ).order_by(MonthlyOverall.year, MonthlyOverall.month).all()

    if granularity == "yearly":
        yearly_rows = db.query(
            MonthlyOverall.year,
            func.sum(MonthlyOverall.total_sales).label("total_sales"),
            func.sum(MonthlyOverall.nev_sales).label("nev_sales"),
        ).filter(
            MonthlyOverall.year >= start_year,
            MonthlyOverall.data_type == "retail",
        ).group_by(MonthlyOverall.year).order_by(MonthlyOverall.year).all()

        data = []
        for r in yearly_rows:
            total = float(r.total_sales or 0)
            nev = float(r.nev_sales or 0)
            rate = (nev / total * 100) if total else 0
            data.append({"year": r.year, "nev_penetration_rate": round(rate, 2), "total_sales": total, "nev_sales": nev})
    else:
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
    year: int = Query(...),
    month: int = Query(...),
    db: Session = Depends(get_db),
):
    row = db.query(MonthlyOverall).filter(
        MonthlyOverall.year == year,
        MonthlyOverall.month == month,
        MonthlyOverall.data_type == "retail",
    ).first()
    if not row:
        return success(None)

    total = float(row.total_sales) if row.total_sales else 0
    data = {
        "year": year,
        "month": month,
        "total_sales": total,
        "nev_sales": float(row.nev_sales) if row.nev_sales else 0,
        "nev_penetration_rate": float(row.nev_penetration_rate) if row.nev_penetration_rate else 0,
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
    years: int = Query(3),
    granularity: str = Query("monthly"),
    db: Session = Depends(get_db),
):
    now = datetime.now()
    start_year = now.year - years + 1

    rows = db.query(MonthlyOverall).filter(
        MonthlyOverall.year >= start_year,
        MonthlyOverall.data_type == "retail",
    ).order_by(MonthlyOverall.year, MonthlyOverall.month).all()

    if granularity == "yearly":
        yearly_rows = db.query(
            MonthlyOverall.year,
            func.sum(MonthlyOverall.nev_sales).label("nev_sales"),
            func.sum(MonthlyOverall.bev_sales).label("bev_sales"),
            func.sum(MonthlyOverall.phev_sales).label("phev_sales"),
            func.sum(MonthlyOverall.hybrid_sales).label("hybrid_sales"),
        ).filter(
            MonthlyOverall.year >= start_year,
            MonthlyOverall.data_type == "retail",
        ).group_by(MonthlyOverall.year).order_by(MonthlyOverall.year).all()

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
    year: int = Query(...),
    month: int = Query(...),
    db: Session = Depends(get_db),
):
    row = db.query(MonthlyOverall).filter(
        MonthlyOverall.year == year,
        MonthlyOverall.month == month,
        MonthlyOverall.data_type == "retail",
    ).first()
    if not row:
        return success(None)

    nev = float(row.nev_sales) if row.nev_sales else 0
    bev = float(row.bev_sales) if row.bev_sales else 0
    phev = float(row.phev_sales) if row.phev_sales else 0
    hybrid = float(row.hybrid_sales) if row.hybrid_sales else 0

    return success({
        "year": year, "month": month,
        "nev_sales": nev,
        "bev_sales": bev, "bev_ratio": round(bev / nev * 100, 2) if nev else 0,
        "phev_sales": phev, "phev_ratio": round(phev / nev * 100, 2) if nev else 0,
        "hybrid_sales": hybrid, "hybrid_ratio": round(hybrid / nev * 100, 2) if nev else 0,
        "ice_sales": float(row.ice_sales) if row.ice_sales else 0,
    })