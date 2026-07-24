from sqlmodel import SQLModel, Field
from sqlalchemy import UniqueConstraint, Column, Numeric, Enum as SAEnum


class SalesData(SQLModel, table=True):
    __tablename__ = "sales_data"
    __table_args__ = (
        UniqueConstraint(
            "year", "month", "data_type", "date_type", "level_type",
            name="uk_sales_data_unique",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    year: int
    month: int
    sales: float | None = Field(default=None, sa_column=Column(Numeric(15, 2)))
    data_type: str | None = Field(
        default="retail",
        sa_column=Column(SAEnum("retail", "production", "export"), default="retail"),
    )
    date_type: str | None = Field(
        default="monthly",
        sa_column=Column(SAEnum("monthly", "quarterly", "yearly"), default="monthly"),
    )
    level_type: str | None = Field(
        default="all",
        sa_column=Column(SAEnum("all", "nev", "bev"), default="all"),
    )