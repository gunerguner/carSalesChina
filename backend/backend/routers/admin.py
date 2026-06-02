from fastapi import APIRouter, Depends

from backend.core.csrf import verify_csrf
from backend.core.deps import DbSession
from backend.core.decorators import handle_try_catch_action
from backend.services.import_service import refresh_brand_meta, refresh_origin_data, refresh_sales_data

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["admin"],
    dependencies=[Depends(verify_csrf)],
)


@router.post("/data/refresh/sales")
@handle_try_catch_action
def trigger_refresh_sales(
    db: DbSession,
):
    return refresh_sales_data(db)


@router.post("/data/refresh/brand-meta")
@handle_try_catch_action
def trigger_refresh_brand_meta(
    db: DbSession,
):
    return refresh_brand_meta(db)


@router.post("/data/refresh/origin")
@handle_try_catch_action
def trigger_refresh_origin(
    db: DbSession,
):
    return refresh_origin_data(db)
