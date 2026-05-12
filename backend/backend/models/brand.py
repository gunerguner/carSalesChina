from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field
from sqlalchemy import UniqueConstraint, Index, Column, Numeric, String, DateTime, Enum as SAEnum, func


class BrandMeta(SQLModel, table=True):
    __tablename__ = "brand_meta"
    __table_args__ = (
        UniqueConstraint("brand_name", name="uk_brand_name"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    brand_name: str = Field(sa_column=Column(String(100), nullable=False))
    brand_name_en: Optional[str] = Field(default=None, sa_column=Column(String(100)))
    master_id: Optional[int] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime, server_default=func.now()))


class BrandSales(SQLModel, table=True):
    __tablename__ = "brand_sales"
    __table_args__ = (
        UniqueConstraint("year", "month", "brand_id", "data_type", name="uk_year_month_brand_type"),
        Index("idx_brand_id", "brand_id"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    year: int
    month: int
    brand_id: int = Field(foreign_key="brand_meta.id")
    sales_volume: Optional[float] = Field(default=None, sa_column=Column(Numeric(15, 2)))
    data_type: Optional[str] = Field(default="retail", sa_column=Column(SAEnum("retail", "wholesale", "production"), default="retail"))
    created_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime, server_default=func.now()))
