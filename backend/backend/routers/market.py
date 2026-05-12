from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlmodel import Session, select

from backend.core.database import get_db
from backend.models.overall import SalesData
from backend.schemas.market import OverviewQuery, TrendQuery, YearlyQuery
from backend.schemas.response import success

router = APIRouter(prefix="/api/v1/market", tags=["market"])

DATA_TYPE_ENUM = Query("retail", pattern="^(retail|production)$")


def _get_sales_by_level(
    db: Session, year: int, month: int, data_type: str, date_type: str
) -> dict[str, float]:
    rows = db.exec(
        select(SalesData).where(
            SalesData.year == year,
            SalesData.month == month,
            SalesData.data_type == data_type,
            SalesData.date_type == date_type,
        )
    ).all()
    result = {}
    for row in rows:
        if row.level_type and row.sales is not None:
            result[row.level_type] = float(row.sales)
    return result


def _get_prev_period(year: int, month: int, date_type: str) -> tuple[int, int]:
    if date_type == "monthly":
        if month > 1:
            return year, month - 1
        return year - 1, 12
    elif date_type == "quarterly":
        if month > 1:
            return year, month - 1
        return year - 1, 4
    else:
        return year - 1, 0


@router.get("/overview")
def overview(
    query: OverviewQuery = Depends(),
    db: Session = Depends(get_db),
):
    sales_map = _get_sales_by_level(
        db, query.year, query.month, query.data_type, query.date_type
    )

    current_val = sales_map.get(query.level_type, 0)

    prev_year, prev_month = _get_prev_period(query.year, query.month, query.date_type)
    prev_period_map = _get_sales_by_level(
        db, prev_year, prev_month, query.data_type, query.date_type
    )
    prev_period_val = prev_period_map.get(query.level_type, 0)

    prev_year_map = _get_sales_by_level(
        db, query.year - 1, query.month, query.data_type, query.date_type
    )
    prev_year_val = prev_year_map.get(query.level_type, 0)

    mom_growth = (
        ((current_val - prev_period_val) / prev_period_val * 100)
        if prev_period_val
        else None
    )
    yoy_growth = (
        ((current_val - prev_year_val) / prev_year_val * 100)
        if prev_year_val
        else None
    )

    total_sales = sales_map.get("all", 0)
    nev_sales = sales_map.get("nev", 0)
    nev_penetration_rate = (nev_sales / total_sales * 100) if total_sales else 0

    return success({
        "year": query.year,
        "month": query.month,
        "data_type": query.data_type,
        "date_type": query.date_type,
        "level_type": query.level_type,
        "sales": current_val,
        "mom_growth": round(mom_growth, 2) if mom_growth is not None else None,
        "yoy_growth": round(yoy_growth, 2) if yoy_growth is not None else None,
        "total_sales": total_sales,
        "nev_sales": nev_sales,
        "bev_sales": sales_map.get("bev", 0),
        "nev_penetration_rate": round(nev_penetration_rate, 2),
    })


@router.get("/trend")
def trend(
    query: TrendQuery = Depends(),
    db: Session = Depends(get_db),
):
    now = datetime.now()
    start_year = now.year - query.years + 1

    if query.granularity == "yearly":
        rows = db.exec(
            select(
                SalesData.year,
                func.sum(SalesData.sales).label("sales"),
            )
            .where(
                SalesData.year >= start_year,
                SalesData.data_type == query.data_type,
                SalesData.date_type == query.date_type,
                SalesData.level_type == query.level_type,
            )
            .group_by(SalesData.year)
            .order_by(SalesData.year)
        ).all()

        data = [{"year": r.year, "sales": float(r.sales or 0)} for r in rows]
    else:
        rows = db.exec(
            select(SalesData)
            .where(
                SalesData.year >= start_year,
                SalesData.data_type == query.data_type,
                SalesData.date_type == query.date_type,
                SalesData.level_type == query.level_type,
            )
            .order_by(SalesData.year, SalesData.month)
        ).all()

        data = [
            {"year": r.year, "month": r.month, "sales": float(r.sales or 0)}
            for r in rows
        ]

    return success(data)


@router.get("/yearly")
def yearly(
    query: YearlyQuery = Depends(),
    db: Session = Depends(get_db),
):
    min_year = db.execute(
        select(func.min(SalesData.year)).where(
            SalesData.data_type == query.data_type,
            SalesData.date_type == query.date_type,
            SalesData.level_type == query.level_type,
        )
    ).scalar() or query.year - 2

    rows = db.exec(
        select(SalesData)
        .where(
            SalesData.year >= min_year,
            SalesData.data_type == query.data_type,
            SalesData.date_type == query.date_type,
            SalesData.level_type == query.level_type,
        )
        .order_by(SalesData.year, SalesData.month)
    ).all()

    all_rows_map = {(r.year, r.month): r for r in rows}

    data = []
    for r in rows:
        prev_year, prev_month = _get_prev_period(r.year, r.month, query.date_type)
        prev_period_row = all_rows_map.get((prev_year, prev_month))
        prev_year_row = all_rows_map.get((r.year - 1, r.month))

        current_val = float(r.sales or 0)
        prev_period_val = float(prev_period_row.sales or 0) if prev_period_row else 0
        prev_year_val = float(prev_year_row.sales or 0) if prev_year_row else 0

        mom_growth = (
            ((current_val - prev_period_val) / prev_period_val * 100)
            if prev_period_val
            else None
        )
        yoy_growth = (
            ((current_val - prev_year_val) / prev_year_val * 100)
            if prev_year_val
            else None
        )

        data.append({
            "year": r.year,
            "month": r.month,
            "sales": current_val,
            "yoy_growth": round(yoy_growth, 2) if yoy_growth is not None else None,
            "mom_growth": round(mom_growth, 2) if mom_growth is not None else None,
        })

    return success(data)


@router.get("/raw")
def raw_all(db: Session = Depends(get_db)):
    """返回全量月度原始数据，供前端本地过滤/聚合，避免每次筛选重复请求。"""
    rows = db.exec(
        select(SalesData)
        .where(SalesData.date_type == "monthly")
        .order_by(SalesData.year, SalesData.month, SalesData.level_type)
    ).all()
    return success([
        {
            "year": r.year,
            "month": r.month,
            "data_type": r.data_type,
            "level_type": r.level_type,
            "sales": float(r.sales or 0),
        }
        for r in rows
    ])