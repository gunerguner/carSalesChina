from sqlmodel import Session, select

from backend.models.overall import SalesData


def get_raw_market_data(db: Session) -> list[dict]:
    rows = db.exec(
        select(SalesData)
        .where(SalesData.date_type == "monthly")
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
