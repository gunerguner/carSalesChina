from typing import Optional

from sqlmodel import SQLModel, Field
from sqlalchemy import UniqueConstraint, Index, Column, Numeric, String, Enum as SAEnum


class OriginShareData(SQLModel, table=True):
    __tablename__ = "origin_share_data"
    __table_args__ = (
        UniqueConstraint("year", "month", "origin", "data_type", name="uk_year_month_origin_type"),
        Index("idx_year_month", "year", "month"),
        Index("idx_origin", "origin"),
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    year: int
    month: int
    origin: str = Field(sa_column=Column(String(20), nullable=False))
    sales_volume: Optional[float] = Field(default=None, sa_column=Column(Numeric(15, 4)))
    data_type: Optional[str] = Field(default="retail", sa_column=Column(SAEnum("retail", "wholesale"), default="retail"))
