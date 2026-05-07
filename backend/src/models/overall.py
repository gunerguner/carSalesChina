from sqlalchemy import Column, BigInteger, Integer, Numeric, String, Enum, DateTime
from sqlalchemy.sql import func

from backend.core.database import Base


class MonthlyOverall(Base):
    __tablename__ = "monthly_overall"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    total_sales = Column(Numeric(15, 2))
    nev_sales = Column(Numeric(15, 2))
    ice_sales = Column(Numeric(15, 2))
    bev_sales = Column(Numeric(15, 2))
    phev_sales = Column(Numeric(15, 2))
    hybrid_sales = Column(Numeric(15, 2))
    nev_penetration_rate = Column(Numeric(5, 2))
    data_type = Column(Enum("retail", "wholesale"), default="retail")
    source = Column(String(50), default="cpca")
    created_at = Column(DateTime, server_default=func.now())