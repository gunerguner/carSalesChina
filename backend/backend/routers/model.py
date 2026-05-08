from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.model import MonthlyModel
from backend.schemas.response import success

router = APIRouter(prefix="/api/v1/models", tags=["models"])


@router.get("/ranking")
def ranking(
    year: int = Query(...),
    month: int = Query(...),
    page: int = Query(1),
    pageSize: int = Query(20),
    energy_type: str = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(MonthlyModel).filter(
        MonthlyModel.year == year,
        MonthlyModel.month == month,
    )
    if energy_type:
        query = query.filter(MonthlyModel.energy_type == energy_type)

    total = query.count()
    rows = query.order_by(MonthlyModel.rank).offset((page - 1) * pageSize).limit(pageSize).all()

    data = []
    for r in rows:
        data.append({
            "id": r.id,
            "model_name": r.model_name,
            "brand_id": r.brand_id,
            "sales_volume": float(r.sales_volume) if r.sales_volume else 0,
            "rank": r.rank,
            "segment": r.segment,
            "energy_type": r.energy_type,
        })

    return success({"total": total, "page": page, "pageSize": pageSize, "data": data})