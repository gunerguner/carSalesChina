from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from backend.core.database import get_db
from backend.services.import_service import refresh_brand_meta, refresh_origin_data, refresh_sales_data
from backend.services.admin_service import get_collection_logs
from backend.schemas.response import success, error

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.post("/data/refresh/sales")
def trigger_refresh_sales(
    db: Session = Depends(get_db),
):
    try:
        result = refresh_sales_data(db)
        return success(result)
    except Exception as e:
        return error(str(e))


@router.post("/data/refresh/brand-meta")
def trigger_refresh_brand_meta(
    db: Session = Depends(get_db),
):
    try:
        result = refresh_brand_meta(db)
        return success(result)
    except Exception as e:
        return error(str(e))


@router.post("/data/refresh/origin")
def trigger_refresh_origin(
    db: Session = Depends(get_db),
):
    try:
        result = refresh_origin_data(db)
        return success(result)
    except Exception as e:
        return error(str(e))


@router.get("/collection/logs")
def collection_logs(
    task_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1),
    pageSize: int = Query(20),
    db: Session = Depends(get_db),
):
    data = get_collection_logs(
        db=db,
        task_type=task_type,
        status=status,
        page=page,
        page_size=pageSize,
    )
    return success(data)
