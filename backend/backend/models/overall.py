from sqlalchemy import Column, BigInteger, Integer, Numeric, Enum, DateTime
from sqlalchemy.sql import func

from backend.core.database import Base


class SalesData(Base):
    __tablename__ = "sales_data"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    total_sales = Column(Numeric(15, 2))
    nev_sales = Column(Numeric(15, 2))
    ice_sales = Column(Numeric(15, 2))
    bev_sales = Column(Numeric(15, 2))
    phev_sales = Column(Numeric(15, 2))
    hybrid_sales = Column(Numeric(15, 2))
    data_type = Column(Enum("retail", "wholesale", "production"), default="retail")
    created_at = Column(DateTime, server_default=func.now())