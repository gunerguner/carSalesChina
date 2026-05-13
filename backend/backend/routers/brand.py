from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from backend.core.database import get_db
from backend.models.brand import BrandSales, BrandMeta
from backend.schemas.brand import TrendAllPeriodsQuery
from backend.schemas.response import success

router = APIRouter(prefix="/api/v1/brands", tags=["brands"])


@router.get("/meta/all")
def meta_all(db: Session = Depends(get_db)):
    rows = db.exec(select(BrandMeta).order_by(BrandMeta.brand_name.asc())).all()
    data = [
        {
            "brand_id": row.id,
            "brand_name": row.brand_name,
        }
        for row in rows
        if row.brand_name
    ]
    return success(data)


@router.get("/trend-all-periods")
def trend_all_periods(
    query: TrendAllPeriodsQuery = Depends(),
    db: Session = Depends(get_db),
):
    names = [x.strip() for x in query.brand_names.split(",") if x.strip()][:3]
    if len(names) == 0:
        return success([])

    metas = db.exec(
        select(BrandMeta).where(BrandMeta.brand_name.in_(names))
    ).all()
    id_to_name = {m.id: m.brand_name for m in metas}
    ids = list(id_to_name.keys())

    if len(ids) == 0:
        return success([])

    rows = db.exec(
        select(BrandSales).where(
            BrandSales.brand_id.in_(ids),
            BrandSales.data_type == query.data_type,
            BrandSales.level_type == "all",
            BrandSales.date_type == "monthly",
        ).order_by(BrandSales.year, BrandSales.month)
    ).all()

    data = {name: {"brand_name": name, "monthly_data": []} for name in names}
    for r in rows:
        brand_name = id_to_name.get(r.brand_id)
        if brand_name is None:
            continue
        data.setdefault(brand_name, {"brand_name": brand_name, "monthly_data": []})
        data[brand_name]["monthly_data"].append(
            {
                "year": r.year,
                "month": r.month,
                "sales": float(r.sales_volume or 0),
            }
        )

    return success([data[name] for name in names])


