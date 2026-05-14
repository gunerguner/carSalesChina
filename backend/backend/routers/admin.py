from fastapi import APIRouter, Depends
from sqlmodel import Session

from backend.core.database import get_db
from backend.core.decorators import handle_try_catch_action
from backend.services.import_service import refresh_brand_meta, refresh_origin_data, refresh_sales_data

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.post("/data/refresh/sales")
@handle_try_catch_action
def trigger_refresh_sales(
    db: Session = Depends(get_db),
):
    return refresh_sales_data(db)


@router.post("/data/refresh/brand-meta")
@handle_try_catch_action
def trigger_refresh_brand_meta(
    db: Session = Depends(get_db),
):
    return refresh_brand_meta(db)


@router.post("/data/refresh/origin")
@handle_try_catch_action
def trigger_refresh_origin(
    db: Session = Depends(get_db),
):
    return refresh_origin_data(db)
