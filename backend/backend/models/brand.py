from sqlmodel import SQLModel, Field
from sqlalchemy import UniqueConstraint, Index, Column, Numeric, String, Enum as SAEnum


class BrandMeta(SQLModel, table=True):
    __tablename__ = "brand_meta"
    __table_args__ = (
        UniqueConstraint("brand_name", name="uk_brand_name"),
    )

    id: int | None = Field(default=None, primary_key=True)
    brand_name: str = Field(sa_column=Column(String(100), nullable=False))
    brand_name_en: str | None = Field(default=None, sa_column=Column(String(100)))
    master_id: int | None = Field(default=None)


class BrandSales(SQLModel, table=True):
    __tablename__ = "brand_sales"
    __table_args__ = (
        UniqueConstraint(
            "year", "month", "brand_id", "data_type", "date_type", "level_type",
            name="uk_brand_sales_unique",
        ),
        Index("idx_brand_id", "brand_id"),
    )

    id: int | None = Field(default=None, primary_key=True)
    year: int
    month: int
    brand_id: int = Field(foreign_key="brand_meta.id")
    sales_volume: float | None = Field(default=None, sa_column=Column(Numeric(15, 2)))
    data_type: str = Field(default="retail", sa_column=Column(SAEnum("retail", "production"), default="retail"))
    date_type: str = Field(
        default="monthly",
        sa_column=Column(SAEnum("monthly", "quarterly", "yearly"), default="monthly"),
    )
    level_type: str = Field(
        default="all",
        sa_column=Column(SAEnum("all", "nev", "bev"), default="all"),
    )
