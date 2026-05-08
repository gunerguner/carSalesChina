from sqlalchemy import Column, BigInteger, Integer, Numeric, String, Enum, DateTime
from sqlalchemy.sql import func

from backend.core.database import Base


class BrandMeta(Base):
    __tablename__ = "brand_meta"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    brand_name = Column(String(100), nullable=False)
    brand_name_en = Column(String(100))
    origin = Column(String(20))
    created_at = Column(DateTime, server_default=func.now())


class BrandSales(Base):
    __tablename__ = "brand_sales"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    brand_name = Column(String(100), nullable=False)
    sales_volume = Column(Numeric(15, 2))
    yoy_growth = Column(Numeric(8, 2))
    mom_growth = Column(Numeric(8, 2))
    data_type = Column(Enum("retail", "wholesale", "production"), default="retail")
    created_at = Column(DateTime, server_default=func.now())