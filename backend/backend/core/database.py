import logging

from sqlmodel import SQLModel, Session, create_engine

from backend.config import DATABASE_URL

logger = logging.getLogger(__name__)

engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20, pool_recycle=3600)


def get_db():
    with Session(engine) as session:
        yield session


def init_db():
    import backend.models  # noqa: F401
    SQLModel.metadata.create_all(bind=engine)
    logger.info("数据库表结构同步完成")
