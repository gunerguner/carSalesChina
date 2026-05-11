from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.log import CollectionLog
from backend.services.import_service import import_cpca_range, import_history, import_monthly_data, upsert_brand_meta
from backend.schemas.response import success, error

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.post("/data/import")
def trigger_import(
    start_year: Optional[int] = Query(None),
    start_month: Optional[int] = Query(None),
    end_year: Optional[int] = Query(None),
    end_month: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    if start_year and start_month and end_year and end_month:
        results = []
        y = start_year
        m = start_month
        while (y, m) <= (end_year, end_month):
            try:
                result = import_monthly_data(db, y, m)
                results.append(result)
            except Exception as e:
                results.append({"year": y, "month": m, "status": "failed", "error": str(e)})
            m += 1
            if m > 12:
                m = 1
                y += 1
        return success(results)
    else:
        results = import_history(db)
        return success(results)


@router.post("/data/import/cpca-history")
def trigger_cpca_history_import(
    start_year: int = Query(2024),
    start_month: int = Query(1),
    end_year: int = Query(2026),
    end_month: int = Query(12),
    db: Session = Depends(get_db),
):
    """批量导入乘联会 2024-2026 月度总体、品牌零售/批发和总体产量数据（不处理 brand_meta）。"""
    try:
        result = import_cpca_range(db, start_year, start_month, end_year, end_month)
        return success(result)
    except Exception as e:
        return error(str(e))


@router.post("/data/import/brand-meta")
def trigger_brand_meta_import(
    db: Session = Depends(get_db),
):
    """根据 meta_data.yaml 中的配置，全量刷新品牌元数据（brand_meta 表）。"""
    try:
        from backend.services.import_service import ORIGIN_MAP
        all_brands = []
        for origin, brands in ORIGIN_MAP.items():
            all_brands.extend(brands)
        count = upsert_brand_meta(db, all_brands)
        return success({"records_count": count, "status": "success"})
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
    query = db.query(CollectionLog)
    if task_type:
        query = query.filter(CollectionLog.task_type == task_type)
    if status:
        query = query.filter(CollectionLog.status == status)

    total = query.count()
    rows = query.order_by(CollectionLog.id.desc()).offset((page - 1) * pageSize).limit(pageSize).all()

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
