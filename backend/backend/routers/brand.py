from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.core.database import get_db
from backend.models.brand import BrandSales, BrandMeta
from backend.models.overall import SalesData
from backend.schemas.response import success

router = APIRouter(prefix="/api/v1/brands", tags=["brands"])

DATA_TYPE_ENUM = Query("retail", pattern="^(retail|wholesale|production)$")


@router.get("/ranking")
def ranking(
    year: int = Query(...),
    month: int = Query(...),
    page: int = Query(1),
    pageSize: int = Query(20),
    origin: str = Query(None),
    data_type: str = DATA_TYPE_ENUM,
    db: Session = Depends(get_db),
):
    subq = db.query(
        BrandSales.brand_name,
        func.sum(BrandSales.sales_volume).label("total_sales"),
    ).filter(
        BrandSales.year == year,
        BrandSales.month == month,
        BrandSales.data_type == data_type,
    ).group_by(BrandSales.brand_name).subquery()

    query = db.query(
        subq.c.brand_name,
        subq.c.total_sales,
        BrandMeta.origin,
    ).outerjoin(
        BrandMeta, BrandMeta.brand_name == subq.c.brand_name
    )

    if origin:
        query = query.filter(BrandMeta.origin == origin)

    total = query.count()
    rows = query.order_by(subq.c.total_sales.desc()).offset((page - 1) * pageSize).limit(pageSize).all()

    data = []
    for idx, r in enumerate(rows, start=(page - 1) * pageSize + 1):
        data.append({
            "rank": idx,
            "brand_name": r.brand_name,
            "sales_volume": float(r.total_sales) if r.total_sales else 0,
            "origin": r.origin,
        })

    return success({"total": total, "page": page, "pageSize": pageSize, "data": data})


@router.get("/ranking/yearly")
def yearly_ranking(
    year: int = Query(...),
    page: int = Query(1),
    pageSize: int = Query(20),
    origin: str = Query(None),
    data_type: str = DATA_TYPE_ENUM,
    db: Session = Depends(get_db),
):
    subq = db.query(
        BrandSales.brand_name,
        func.sum(BrandSales.sales_volume).label("total_sales"),
    ).filter(
        BrandSales.year == year,
        BrandSales.data_type == data_type,
    ).group_by(BrandSales.brand_name).subquery()

    query = db.query(
        subq.c.brand_name,
        subq.c.total_sales,
        BrandMeta.origin,
    ).outerjoin(
        BrandMeta, BrandMeta.brand_name == subq.c.brand_name
    )

    if origin:
        query = query.filter(BrandMeta.origin == origin)

    total = query.count()
    rows = query.order_by(subq.c.total_sales.desc()).offset((page - 1) * pageSize).limit(pageSize).all()

    data = []
    for idx, r in enumerate(rows, start=(page - 1) * pageSize + 1):
        data.append({
            "rank": idx,
            "brand_name": r.brand_name,
            "total_sales": float(r.total_sales or 0),
            "origin": r.origin,
        })

    return success({"total": total, "page": page, "pageSize": pageSize, "data": data})


@router.get("/compare")
def compare(
    brand_names: str = Query(...),
    year: int = Query(...),
    month: int = Query(...),
    data_type: str = DATA_TYPE_ENUM,
    db: Session = Depends(get_db),
):
    names = [x.strip() for x in brand_names.split(",")[:5]]
    rows = db.query(BrandSales).filter(
        BrandSales.brand_name.in_(names),
        BrandSales.year == year,
        BrandSales.month == month,
        BrandSales.data_type == data_type,
    ).all()

    name_to_row = {r.brand_name: r for r in rows}

    data = []
    for name in names:
        r = name_to_row.get(name)
        if r:
            data.append({
                "brand_name": r.brand_name,
                "sales_volume": float(r.sales_volume) if r.sales_volume else 0,
                "yoy_growth": float(r.yoy_growth) if r.yoy_growth else None,
                "mom_growth": float(r.mom_growth) if r.mom_growth else None,
            })

    return success(data)


@router.get("/compare/trend")
def compare_trend(
    brand_names: str = Query(...),
    years: int = Query(3),
    granularity: str = Query("monthly"),
    data_type: str = DATA_TYPE_ENUM,
    db: Session = Depends(get_db),
):
    from datetime import datetime
    now = datetime.now()
    start_year = now.year - years + 1
    names = [x.strip() for x in brand_names.split(",")[:5]]

    if granularity == "yearly":
        result = db.query(
            BrandSales.brand_name,
            BrandSales.year,
            func.sum(BrandSales.sales_volume).label("total_sales"),
        ).filter(
            BrandSales.brand_name.in_(names),
            BrandSales.year >= start_year,
            BrandSales.data_type == data_type,
        ).group_by(BrandSales.brand_name, BrandSales.year).order_by(BrandSales.year).all()

        data = {}
        for r in result:
            if r.brand_name not in data:
                data[r.brand_name] = {"brand_name": r.brand_name, "trend": []}
            data[r.brand_name]["trend"].append({"year": r.year, "sales": float(r.total_sales or 0)})
    else:
        rows = db.query(BrandSales).filter(
            BrandSales.brand_name.in_(names),
            BrandSales.year >= start_year,
            BrandSales.data_type == data_type,
        ).order_by(BrandSales.year, BrandSales.month).all()

        data = {}
        for r in rows:
            if r.brand_name not in data:
                data[r.brand_name] = {"brand_name": r.brand_name, "trend": []}
            data[r.brand_name]["trend"].append({
                "year": r.year, "month": r.month, "sales": float(r.sales_volume or 0),
            })

    return success(list(data.values()))


@router.get("/{brand_name}/detail")
def brand_detail(
    brand_name: str,
    year: int = Query(...),
    month: int = Query(...),
    data_type: str = DATA_TYPE_ENUM,
    db: Session = Depends(get_db),
):
    row = db.query(BrandSales).filter(
        BrandSales.brand_name == brand_name,
        BrandSales.year == year,
        BrandSales.month == month,
        BrandSales.data_type == data_type,
    ).first()

    meta = db.query(BrandMeta).filter(BrandMeta.brand_name == brand_name).first()

    if not row:
        return success(None)

    return success({
        "brand_name": row.brand_name,
        "sales_volume": float(row.sales_volume) if row.sales_volume else 0,
        "yoy_growth": float(row.yoy_growth) if row.yoy_growth else None,
        "mom_growth": float(row.mom_growth) if row.mom_growth else None,
        "origin": meta.origin if meta else None,
    })


@router.get("/{brand_name}/trend")
def brand_trend(
    brand_name: str,
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
            BrandSales.year,
            func.sum(BrandSales.sales_volume).label("total_sales"),
        ).filter(
            BrandSales.brand_name == brand_name,
            BrandSales.year >= start_year,
            BrandSales.data_type == data_type,
        ).group_by(BrandSales.year).order_by(BrandSales.year).all()

        data = [{"year": r.year, "sales": float(r.total_sales or 0)} for r in rows]
    else:
        rows = db.query(BrandSales).filter(
            BrandSales.brand_name == brand_name,
            BrandSales.year >= start_year,
            BrandSales.data_type == data_type,
        ).order_by(BrandSales.year, BrandSales.month).all()

        data = [{"year": r.year, "month": r.month, "sales": float(r.sales_volume or 0)} for r in rows]

    return success(data)