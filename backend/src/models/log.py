from sqlalchemy import Column, BigInteger, Integer, String, Enum, Text, DateTime
from sqlalchemy.sql import func

from backend.src.core.database import Base


class CollectionLog(Base):
    __tablename__ = "data_collection_log"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    task_type = Column(String(50), nullable=False)
    status = Column(Enum("pending", "success", "failed"), default="pending")
    records_count = Column(Integer, default=0)
    error_message = Column(Text)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)