from sqlalchemy import Column, BigInteger, Integer, Numeric, String, SmallInteger, DateTime
from sqlalchemy.sql import func

from backend.core.database import Base


class MonthlyBrand(Base):
    __tablename__ = "monthly_brand"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    brand_name = Column(String(100), nullable=False)
    brand_name_en = Column(String(100))
    sales_volume = Column(Numeric(15, 2))
    rank = Column(Integer)
    prev_month_rank = Column(Integer)
    yoy_growth = Column(Numeric(8, 2))
    mom_growth = Column(Numeric(8, 2))
    is_nev = Column(SmallInteger, default=0)
    source = Column(String(50), default="cpca")
    created_at = Column(DateTime, server_default=func.now())