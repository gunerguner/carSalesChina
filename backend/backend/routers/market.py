from fastapi import APIRouter

from backend.core.decorators import handle_success_response
from backend.core.deps import DbSession
from backend.services.market_service import get_raw_market_data

router = APIRouter(prefix="/api/v1/market", tags=["market"])


@router.get("/raw")
@handle_success_response
def raw_all(db: DbSession):
    """返回全量月度原始数据，供前端本地过滤/聚合，避免每次筛选重复请求。"""
    return get_raw_market_data(db)
