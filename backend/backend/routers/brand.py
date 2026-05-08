from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.core.database import get_db
from backend.models.brand import MonthlyBrand
from backend.models.overall import MonthlyOverall
from backend.schemas.response import success

router = APIRouter(prefix="/api/v1/brands", tags=["brands"])

DATA_TYPE_ENUM = Query("retail", pattern="^(retail|wholesale|production)$")


@router.get("/ranking")
def ranking(
    year: int = Query(...),
    month: int = Query(...),
    page: int = Query(1),
    pageSize: int = Query(20),
    is_nev: int = Query(None),
    data_type: str = DATA_TYPE_ENUM,
    db: Session = Depends(get_db),
):
    query = db.query(MonthlyBrand).filter(
        MonthlyBrand.year == year,
        MonthlyBrand.month == month,
        MonthlyBrand.source == "cpca",
        MonthlyBrand.data_type == data_type,
    )
    if is_nev is not None:
        query = query.filter(MonthlyBrand.is_nev == is_nev)

    total = query.count()
    rows = query.order_by(MonthlyBrand.rank).offset((page - 1) * pageSize).limit(pageSize).all()

    data = []
    for r in rows:
        data.append({
            "id": r.id,
            "brand_name": r.brand_name,
            "brand_name_en": r.brand_name_en,
            "sales_volume": float(r.sales_volume) if r.sales_volume else 0,
            "rank": r.rank,
            "prev_month_rank": r.prev_month_rank,
            "yoy_growth": float(r.yoy_growth) if r.yoy_growth else None,
            "mom_growth": float(r.mom_growth) if r.mom_growth else None,
            "is_nev": r.is_nev,
        })

    return success({"total": total, "page": page, "pageSize": pageSize, "data": data})


@router.get("/ranking/yearly")
def yearly_ranking(
    year: int = Query(...),
    page: int = Query(1),
    pageSize: int = Query(20),
    data_type: str = DATA_TYPE_ENUM,
    db: Session = Depends(get_db),
):
    rows = db.query(
        MonthlyBrand.brand_name,
        func.max(MonthlyBrand.is_nev).label("is_nev"),
        func.sum(MonthlyBrand.sales_volume).label("total_sales"),
    ).filter(
        MonthlyBrand.year == year,
        MonthlyBrand.source == "cpca",
        MonthlyBrand.data_type == data_type,
    ).group_by(MonthlyBrand.brand_name).order_by(func.sum(MonthlyBrand.sales_volume).desc()).all()

    total = len(rows)
    paginated = rows[(page - 1) * pageSize: page * pageSize]

    data = []
    for idx, r in enumerate(paginated, start=(page - 1) * pageSize + 1):
        data.append({
            "rank": idx,
            "brand_name": r.brand_name,
            "total_sales": float(r.total_sales or 0),
            "is_nev": r.is_nev,
        })

    return success({"total": total, "page": page, "pageSize": pageSize, "data": data})


@router.get("/compare")
def compare(
    brand_ids: str = Query(...),
    year: int = Query(...),
    month: int = Query(...),
    data_type: str = DATA_TYPE_ENUM,
    db: Session = Depends(get_db),
):
    ids = [int(x) for x in brand_ids.split(",")[:5]]
    rows = db.query(MonthlyBrand).filter(
        MonthlyBrand.id.in_(ids),
        MonthlyBrand.year == year,
        MonthlyBrand.month == month,
        MonthlyBrand.data_type == data_type,
    ).all()

    data = []
    for r in rows:
        data.append({
            "brand_id": r.id,
            "brand_name": r.brand_name,
            "sales_volume": float(r.sales_volume) if r.sales_volume else 0,
            "rank": r.rank,
            "yoy_growth": float(r.yoy_growth) if r.yoy_growth else None,
            "mom_growth": float(r.mom_growth) if r.mom_growth else None,
        })

    return success(data)


@router.get("/compare/trend")
def compare_trend(
    brand_ids: str = Query(...),
    years: int = Query(3),
    granularity: str = Query("monthly"),
    data_type: str = DATA_TYPE_ENUM,
    db: Session = Depends(get_db),
):
    from datetime import datetime
    now = datetime.now()
    start_year = now.year - years + 1
    ids = [int(x) for x in brand_ids.split(",")[:5]]

    rows = db.query(MonthlyBrand).filter(
        MonthlyBrand.id.in_(ids),
        MonthlyBrand.year >= start_year,
        MonthlyBrand.data_type == data_type,
    ).order_by(MonthlyBrand.year, MonthlyBrand.month).all()

    if granularity == "yearly":
        result = db.query(
            MonthlyBrand.id,
            MonthlyBrand.brand_name,
            MonthlyBrand.year,
            func.sum(MonthlyBrand.sales_volume).label("total_sales"),
        ).filter(
            MonthlyBrand.id.in_(ids),
            MonthlyBrand.year >= start_year,
            MonthlyBrand.data_type == data_type,
        ).group_by(MonthlyBrand.id, MonthlyBrand.brand_name, MonthlyBrand.year).all()

        data = {}
        for r in result:
            if r.brand_name not in data:
                data[r.brand_name] = {"brand_id": r.id, "brand_name": r.brand_name, "trend": []}
            data[r.brand_name]["trend"].append({"year": r.year, "sales": float(r.total_sales or 0)})
    else:
        data = {}
        for r in rows:
            if r.brand_name not in data:
                data[r.brand_name] = {"brand_id": r.id, "brand_name": r.brand_name, "trend": []}
            data[r.brand_name]["trend"].append({
                "year": r.year, "month": r.month, "sales": float(r.sales_volume or 0),
            })

    return success(list(data.values()))


@router.get("/{brand_id}/detail")
def brand_detail(
    brand_id: int,
    year: int = Query(...),
    month: int = Query(...),
    data_type: str = DATA_TYPE_ENUM,
    db: Session = Depends(get_db),
):
    row = db.query(MonthlyBrand).filter(
        MonthlyBrand.id == brand_id,
        MonthlyBrand.year == year,
        MonthlyBrand.month == month,
        MonthlyBrand.data_type == data_type,
    ).first()
    if not row:
        return success(None)

    return success({
        "brand_id": row.id,
        "brand_name": row.brand_name,
        "brand_name_en": row.brand_name_en,
        "sales_volume": float(row.sales_volume) if row.sales_volume else 0,
        "rank": row.rank,
        "prev_month_rank": row.prev_month_rank,
        "yoy_growth": float(row.yoy_growth) if row.yoy_growth else None,
        "mom_growth": float(row.mom_growth) if row.mom_growth else None,
        "is_nev": row.is_nev,
    })


@router.get("/{brand_id}/trend")
def brand_trend(
    brand_id: int,
    years: int = Query(3),
    granularity: str = Query("monthly"),
    data_type: str = DATA_TYPE_ENUM,
    db: Session = Depends(get_db),
):
    from datetime import datetime
    now = datetime.now()
    start_year = now.year - years + 1

    if granularity == "yearly":
        rows = db.query(
            MonthlyBrand.year,
            func.sum(MonthlyBrand.sales_volume).label("total_sales"),
        ).filter(
            MonthlyBrand.id == brand_id,
            MonthlyBrand.year >= start_year,
            MonthlyBrand.data_type == data_type,
        ).group_by(MonthlyBrand.year).order_by(MonthlyBrand.year).all()

        data = [{"year": r.year, "sales": float(r.total_sales or 0)} for r in rows]
    else:
        rows = db.query(MonthlyBrand).filter(
            MonthlyBrand.id == brand_id,
            MonthlyBrand.year >= start_year,
            MonthlyBrand.data_type == data_type,
        ).order_by(MonthlyBrand.year, MonthlyBrand.month).all()

        data = [{"year": r.year, "month": r.month, "sales": float(r.sales_volume or 0)} for r in rows]

    return success(data)
