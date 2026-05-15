from sqlmodel import Session, select

from backend.core.exceptions import ValidationAppError
from backend.models.overall import SalesData


def get_raw_market_data(db: Session, *, date_type: str = "monthly") -> list[dict]:
    if date_type not in {"monthly", "yearly", "quarterly"}:
        raise ValidationAppError("date_type 仅支持 monthly、quarterly、yearly")

    rows = db.exec(
        select(SalesData)
        .where(SalesData.date_type == date_type)
        .order_by(SalesData.year, SalesData.month, SalesData.level_type)
    ).all()
    return [
        {
            "year": row.year,
            "month": row.month,
            "data_type": row.data_type,
            "level_type": row.level_type,
            "sales": float(row.sales or 0),
        }
        for row in rows
    ]
