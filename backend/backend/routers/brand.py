from fastapi import APIRouter, Depends
from sqlmodel import Session

from backend.core.database import get_db
from backend.schemas.brand import TrendAllPeriodsQuery
from backend.schemas.response import success
from backend.services.brand_service import get_all_brand_meta, get_brand_trend_all_periods

router = APIRouter(prefix="/api/v1/brands", tags=["brands"])


@router.get("/meta/all")
def meta_all(db: Session = Depends(get_db)):
    data = get_all_brand_meta(db)
    return success(data)


@router.get("/trend-all-periods")
def trend_all_periods(
    query: TrendAllPeriodsQuery = Depends(),
    db: Session = Depends(get_db),
):
    data = get_brand_trend_all_periods(
        db=db,
        brand_names=query.brand_names,
        data_type=query.data_type,
    )
    return success(data)
