from fastapi import APIRouter, Depends
from sqlmodel import Session

from backend.core.database import get_db
from backend.schemas.response import success
from backend.services.market_service import get_raw_market_data

router = APIRouter(prefix="/api/v1/market", tags=["market"])


@router.get("/raw")
def raw_all(db: Session = Depends(get_db)):
    """返回全量月度原始数据，供前端本地过滤/聚合，避免每次筛选重复请求。"""
    data = get_raw_market_data(db)
    return success(data)
