from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Integer, Text, Enum as SAEnum


class CollectionLog(SQLModel, table=True):
    __tablename__ = "data_collection_log"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_type: str = Field(sa_column=Column(String(50), nullable=False))
    status: Optional[str] = Field(default="pending", sa_column=Column(SAEnum("pending", "success", "failed"), default="pending"))
    records_count: Optional[int] = Field(default=0, sa_column=Column(Integer, default=0))
    error_message: Optional[str] = Field(default=None, sa_column=Column(Text))
    started_at: Optional[datetime] = Field(default=None)
    finished_at: Optional[datetime] = Field(default=None)
