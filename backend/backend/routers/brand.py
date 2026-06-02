from typing import Annotated

from fastapi import APIRouter, Query

from backend.core.decorators import handle_success_response
from backend.core.deps import DbSession
from backend.schemas.brand import TrendAllPeriodsQuery
from backend.services.brand_service import get_all_brand_meta, get_brand_trend_all_periods

router = APIRouter(prefix="/api/v1/brands", tags=["brands"])


@router.get("/meta/all")
@handle_success_response
def meta_all(db: DbSession):
    return get_all_brand_meta(db)


@router.get("/trend-all-periods")
@handle_success_response
def trend_all_periods(
    query: Annotated[TrendAllPeriodsQuery, Query()],
    db: DbSession,
):
    return get_brand_trend_all_periods(
        db=db,
        brand_names=query.brand_names,
        data_type=query.data_type,
    )
