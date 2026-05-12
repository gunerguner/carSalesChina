from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlmodel import Session, select

from backend.core.database import get_db
from backend.models.brand import BrandSales, BrandMeta
from backend.schemas.brand import (
    CompareTrendQuery,
    RankingQuery,
    YearlyRankingQuery,
)
from backend.schemas.response import success

router = APIRouter(prefix="/api/v1/brands", tags=["brands"])

DATA_TYPE_ENUM = Query("retail", pattern="^(retail|wholesale|production)$")


@router.get("/ranking")
def ranking(
    query: RankingQuery = Depends(),
    db: Session = Depends(get_db),
):
    subq = select(
        BrandSales.brand_id,
        func.sum(BrandSales.sales_volume).label("total_sales"),
    ).where(
        BrandSales.year == query.year,
        BrandSales.month == query.month,
        BrandSales.data_type == query.data_type,
        BrandSales.level_type == query.level_type,
    ).group_by(BrandSales.brand_id).subquery()

    query_sql = select(
        BrandMeta.brand_name,
        subq.c.total_sales,
    ).select_from(subq).join(
        BrandMeta, BrandMeta.id == subq.c.brand_id
    )

    total = db.execute(select(func.count()).select_from(subq)).scalar()
    rows = db.exec(query_sql.order_by(subq.c.total_sales.desc()).offset((query.page - 1) * query.pageSize).limit(query.pageSize)).all()

    data = []
    for idx, r in enumerate(rows, start=(query.page - 1) * query.pageSize + 1):
        data.append({
            "rank": idx,
            "brand_name": r.brand_name,
            "sales_volume": float(r.total_sales) if r.total_sales else 0,
        })

    return success({"total": total, "page": query.page, "pageSize": query.pageSize, "data": data})


@router.get("/ranking/yearly")
def yearly_ranking(
    query: YearlyRankingQuery = Depends(),
    db: Session = Depends(get_db),
):
    subq = select(
        BrandSales.brand_id,
        func.sum(BrandSales.sales_volume).label("total_sales"),
    ).where(
        BrandSales.year == query.year,
        BrandSales.data_type == query.data_type,
        BrandSales.level_type == query.level_type,
    ).group_by(BrandSales.brand_id).subquery()

    query_sql = select(
        BrandMeta.brand_name,
        subq.c.total_sales,
    ).select_from(subq).join(
        BrandMeta, BrandMeta.id == subq.c.brand_id
    )

    total = db.execute(select(func.count()).select_from(subq)).scalar()
    rows = db.exec(query_sql.order_by(subq.c.total_sales.desc()).offset((query.page - 1) * query.pageSize).limit(query.pageSize)).all()

    data = []
    for idx, r in enumerate(rows, start=(query.page - 1) * query.pageSize + 1):
        data.append({
            "rank": idx,
            "brand_name": r.brand_name,
            "total_sales": float(r.total_sales or 0),
        })

    return success({"total": total, "page": query.page, "pageSize": query.pageSize, "data": data})





@router.get("/compare/trend")
def compare_trend(
    query: CompareTrendQuery = Depends(),
    db: Session = Depends(get_db),
):
    now = datetime.now()
    start_year = now.year - query.years + 1
    names = [x.strip() for x in query.brand_names.split(",")[:5]]

    metas = db.exec(select(BrandMeta).where(BrandMeta.brand_name.in_(names))).all()
    name_to_id = {m.brand_name: m.id for m in metas}
    id_to_name = {m.id: m.brand_name for m in metas}
    ids = list(id_to_name.keys())

    if query.granularity == "yearly":
        result = db.exec(select(
            BrandSales.brand_id,
            BrandSales.year,
            func.sum(BrandSales.sales_volume).label("total_sales"),
        ).where(
            BrandSales.brand_id.in_(ids),
            BrandSales.year >= start_year,
            BrandSales.data_type == query.data_type,
            BrandSales.level_type == query.level_type,
        ).group_by(BrandSales.brand_id, BrandSales.year).order_by(BrandSales.year)).all()

        data = {}
        for r in result:
            bname = id_to_name.get(r.brand_id, str(r.brand_id))
            if bname not in data:
                data[bname] = {"brand_name": bname, "trend": []}
            data[bname]["trend"].append({"year": r.year, "sales": float(r.total_sales or 0)})
    else:
        rows = db.exec(select(BrandSales).where(
            BrandSales.brand_id.in_(ids),
            BrandSales.year >= start_year,
            BrandSales.data_type == query.data_type,
            BrandSales.level_type == query.level_type,
        ).order_by(BrandSales.year, BrandSales.month)).all()

        data = {}
        for r in rows:
            bname = id_to_name.get(r.brand_id, str(r.brand_id))
            if bname not in data:
                data[bname] = {"brand_name": bname, "trend": []}
            data[bname]["trend"].append({
                "year": r.year, "month": r.month, "sales": float(r.sales_volume or 0),
            })

    return success(list(data.values()))






