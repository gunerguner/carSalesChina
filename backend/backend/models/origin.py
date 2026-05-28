from sqlmodel import SQLModel, Field
from sqlalchemy import UniqueConstraint, Index, Column, Numeric, String


class OriginShareData(SQLModel, table=True):
    __tablename__ = "origin_share_data"
    __table_args__ = (
        UniqueConstraint("year", "month", "origin", name="uk_year_month_origin"),
        Index("idx_year_month", "year", "month"),
        Index("idx_origin", "origin"),
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id: int | None = Field(default=None, primary_key=True)
    year: int
    month: int
    origin: str = Field(sa_column=Column(String(20), nullable=False))
    sales_volume: float | None = Field(default=None, sa_column=Column(Numeric(15, 4)))
