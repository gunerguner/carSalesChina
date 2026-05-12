from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field
from sqlalchemy import UniqueConstraint, Column, Numeric, DateTime, Enum as SAEnum, func


class SalesData(SQLModel, table=True):
    __tablename__ = "sales_data"
    __table_args__ = (
        UniqueConstraint(
            "year", "month", "data_type", "date_type", "level_type",
            name="uk_sales_data_unique",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    year: int
    month: int
    sales: Optional[float] = Field(default=None, sa_column=Column(Numeric(15, 2)))
    data_type: Optional[str] = Field(
        default="retail",
        sa_column=Column(SAEnum("retail", "production"), default="retail"),
    )
    date_type: Optional[str] = Field(
        default="monthly",
        sa_column=Column(SAEnum("monthly", "quarterly", "yearly"), default="monthly"),
    )
    level_type: Optional[str] = Field(
        default="all",
        sa_column=Column(SAEnum("all", "nev", "bev"), default="all"),
    )
    created_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime, server_default=func.now())
    )