from sqlalchemy import Column, BigInteger, Integer, Numeric, String, DateTime
from sqlalchemy.sql import func

from backend.src.core.database import Base


class MonthlyModel(Base):
    __tablename__ = "monthly_model"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    model_name = Column(String(200), nullable=False)
    brand_id = Column(BigInteger)
    sales_volume = Column(Numeric(15, 2))
    rank = Column(Integer)
    segment = Column(String(50))
    energy_type = Column(String(20))
    source = Column(String(50), default="cpca")
    created_at = Column(DateTime, server_default=func.now())