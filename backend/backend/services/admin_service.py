from typing import Any

from sqlalchemy import func
from sqlmodel import Session, select

from backend.models.log import CollectionLog


def _serialize_log(row: CollectionLog) -> dict[str, Any]:
    return {
        "id": row.id,
        "task_type": row.task_type,
        "status": row.status,
        "records_count": row.records_count,
        "error_message": row.error_message,
        "started_at": row.started_at.isoformat() if row.started_at else None,
        "finished_at": row.finished_at.isoformat() if row.finished_at else None,
    }


def get_collection_logs(
    db: Session,
    task_type: str | None,
    status: str | None,
    page: int,
    page_size: int,
) -> dict[str, Any]:
    filters = []
    if task_type:
        filters.append(CollectionLog.task_type == task_type)
    if status:
        filters.append(CollectionLog.status == status)

    total = db.exec(
        select(func.count()).select_from(CollectionLog).where(*filters)
    ).one()
    rows = db.exec(
        select(CollectionLog)
        .where(*filters)
        .order_by(CollectionLog.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return {
        "total": total,
        "page": page,
        "pageSize": page_size,
        "data": [_serialize_log(row) for row in rows],
    }
