from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from backend.core.database import get_db
from backend.models.overall import SalesData
from backend.schemas.response import success

router = APIRouter(prefix="/api/v1/market", tags=["market"])


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
