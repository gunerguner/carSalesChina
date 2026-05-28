from sqlmodel import Session, select

from backend.common.types import MarketRawRow
from backend.models.overall import SalesData


def get_raw_market_data(db: Session, *, date_type: str = "monthly") -> list[MarketRawRow]:
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
