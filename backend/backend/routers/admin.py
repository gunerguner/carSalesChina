from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, func

from backend.core.database import get_db
from backend.models.log import CollectionLog
from backend.services.import_service import refresh_brand_meta, refresh_all_sales_data, refresh_total_sales_data
from backend.schemas.response import success, error

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.post("/data/refresh/sales")
def trigger_refresh_sales(
    db: Session = Depends(get_db),
):
    try:
        result = refresh_all_sales_data(db)
        return success(result)
    except Exception as e:
        return error(str(e))


@router.post("/data/refresh/total-sales")
def trigger_refresh_total_sales(
    db: Session = Depends(get_db),
):
    try:
        result = refresh_total_sales_data(db)
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


@router.get("/collection/logs")
def collection_logs(
    task_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1),
    pageSize: int = Query(20),
    db: Session = Depends(get_db),
):
    query = select(CollectionLog)
    if task_type:
        query = query.where(CollectionLog.task_type == task_type)
    if status:
        query = query.where(CollectionLog.status == status)

    total = db.execute(select(func.count()).select_from(CollectionLog).where(
        CollectionLog.task_type == task_type if task_type else True,
        CollectionLog.status == status if status else True,
    )).scalar()

    rows = db.exec(query.order_by(CollectionLog.id.desc()).offset((page - 1) * pageSize).limit(pageSize)).all()

    data = []
    for r in rows:
        data.append({
            "id": r.id,
            "task_type": r.task_type,
            "status": r.status,
            "records_count": r.records_count,
            "error_message": r.error_message,
            "started_at": r.started_at.isoformat() if r.started_at else None,
            "finished_at": r.finished_at.isoformat() if r.finished_at else None,
        })

    return success({"total": total, "page": page, "pageSize": pageSize, "data": data})
