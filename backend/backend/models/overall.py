from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field
from sqlalchemy import UniqueConstraint, Column, Numeric, DateTime, Enum as SAEnum, func


class SalesData(SQLModel, table=True):
    __tablename__ = "sales_data"
    __table_args__ = (
        UniqueConstraint("year", "month", "data_type", name="uk_year_month_type"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    year: int
    month: int
    total_sales: Optional[float] = Field(default=None, sa_column=Column(Numeric(15, 2)))
    nev_sales: Optional[float] = Field(default=None, sa_column=Column(Numeric(15, 2)))
    ice_sales: Optional[float] = Field(default=None, sa_column=Column(Numeric(15, 2)))
    bev_sales: Optional[float] = Field(default=None, sa_column=Column(Numeric(15, 2)))
    phev_sales: Optional[float] = Field(default=None, sa_column=Column(Numeric(15, 2)))
    hybrid_sales: Optional[float] = Field(default=None, sa_column=Column(Numeric(15, 2)))
    data_type: Optional[str] = Field(default="retail", sa_column=Column(SAEnum("retail", "wholesale", "production"), default="retail"))
    created_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime, server_default=func.now()))
