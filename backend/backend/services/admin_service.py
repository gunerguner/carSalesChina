from typing import Any

from sqlalchemy import func
from sqlmodel import Session, select

from backend.models.log import CollectionLog


def get_collection_logs(
    db: Session,
    task_type: str | None,
    status: str | None,
    page: int,
    page_size: int,
) -> dict[str, Any]:
    query = select(CollectionLog)
    if task_type:
        query = query.where(CollectionLog.task_type == task_type)
    if status:
        query = query.where(CollectionLog.status == status)

    total = db.execute(
        select(func.count()).select_from(CollectionLog).where(
            CollectionLog.task_type == task_type if task_type else True,
            CollectionLog.status == status if status else True,
        )
    ).scalar()

    rows = db.exec(
        query.order_by(CollectionLog.id.desc()).offset((page - 1) * page_size).limit(page_size)
    ).all()

    data = []
    for row in rows:
        data.append(
            {
                "id": row.id,
                "task_type": row.task_type,
                "status": row.status,
                "records_count": row.records_count,
                "error_message": row.error_message,
                "started_at": row.started_at.isoformat() if row.started_at else None,
                "finished_at": row.finished_at.isoformat() if row.finished_at else None,
            }
        )

    return {
        "total": total,
        "page": page,
        "pageSize": page_size,
        "data": data,
    }
