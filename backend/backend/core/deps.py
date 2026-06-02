from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from backend.core.database import get_db

DbSession = Annotated[Session, Depends(get_db)]
