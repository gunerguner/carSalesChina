"""pytest 共享夹具。

约定（与生产代码的两个耦合点）：
- ``backend.main`` 在 import 时执行 ``setup_logging()``，会在 LOG_DIR 下建日志文件——
  必须在导入它之前把 ``LOG_DIR``/``LOG_LEVEL`` 指到临时目录，避免污染仓库；
- ``backend.core.database`` 的全局 engine 绑定 MySQL 且带 pool 参数，测试不复用它，
  一律自建 SQLite 内存库；API 测试通过 ``dependency_overrides[get_db]`` 注入。
"""

import os
import tempfile
from datetime import datetime

os.environ.setdefault("LOG_DIR", tempfile.mkdtemp(prefix="carsales-test-logs-"))
os.environ.setdefault("LOG_LEVEL", "WARNING")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

import backend.models  # noqa: F401  # 确保所有表模型注册到 metadata
from backend.models.brand import BrandMeta, BrandSales
from backend.models.origin import OriginShareData
from backend.models.overall import SalesData


@pytest.fixture
def db_engine():
    # StaticPool：所有线程共用同一个连接（TestClient 在线程池中执行 sync 端点），
    # 否则内存 SQLite 会为每个线程分配独立的空库。
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(db_engine):
    with Session(db_engine) as session:
        yield session


@pytest.fixture
def client(db_session):
    """TestClient + SQLite session 注入。

    不进入 ``with`` 上下文（避免 lifespan → init_db 连 MySQL）；
    ``raise_server_exceptions=False`` 使裸 Exception 处理器的 500 信封可被断言。
    """
    from backend.core.database import get_db
    from backend.main import app

    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    try:
        yield TestClient(app, raise_server_exceptions=False)
    finally:
        app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# 种子数据工厂
# ---------------------------------------------------------------------------


def add_sales(
    db: Session,
    *,
    year: int,
    month: int,
    sales: float,
    data_type: str = "retail",
    date_type: str = "monthly",
    level_type: str = "all",
) -> SalesData:
    row = SalesData(
        year=year,
        month=month,
        sales=sales,
        data_type=data_type,
        date_type=date_type,
        level_type=level_type,
    )
    db.add(row)
    return row


def add_brand_meta(
    db: Session, *, brand_name: str, brand_name_en: str, master_id: int | None
) -> BrandMeta:
    row = BrandMeta(brand_name=brand_name, brand_name_en=brand_name_en, master_id=master_id)
    db.add(row)
    db.flush()  # 立即分配主键，供外键引用
    return row


def add_brand_sales(
    db: Session,
    *,
    brand_id: int,
    year: int,
    month: int,
    sales_volume: float,
    data_type: str = "retail",
    date_type: str = "monthly",
    level_type: str = "all",
) -> BrandSales:
    row = BrandSales(
        brand_id=brand_id,
        year=year,
        month=month,
        sales_volume=sales_volume,
        data_type=data_type,
        date_type=date_type,
        level_type=level_type,
    )
    db.add(row)
    return row


def add_origin_share(
    db: Session, *, year: int, month: int, origin: str, sales_volume: float
) -> OriginShareData:
    row = OriginShareData(year=year, month=month, origin=origin, sales_volume=sales_volume)
    db.add(row)
    return row


@pytest.fixture
def analysis_dataset(db_session):
    """经典分析数据集：以当前年份为锚（_start_year 依赖 datetime.now()）。

    monthly retail 行（level: all/nev/bev）：
      (CY-1, 1): 100 / 30 / 10
      (CY-1, 2): 200 / 80 / 20
      (CY,   1): 150 / 60 / 15
    另含应被分析查询排除的 production 行与 quarterly 行。
    """
    cy = datetime.now().year
    monthly = [
        (cy - 1, 1, 100.0, 30.0, 10.0),
        (cy - 1, 2, 200.0, 80.0, 20.0),
        (cy, 1, 150.0, 60.0, 15.0),
    ]
    for year, month, all_s, nev, bev in monthly:
        add_sales(db_session, year=year, month=month, sales=all_s, level_type="all")
        add_sales(db_session, year=year, month=month, sales=nev, level_type="nev")
        add_sales(db_session, year=year, month=month, sales=bev, level_type="bev")
    # 非零售 / 非月度数据不应参与分析聚合
    add_sales(db_session, year=cy - 1, month=1, sales=999.0, data_type="production")
    add_sales(db_session, year=cy - 1, month=1, sales=888.0, date_type="quarterly")
    db_session.commit()
    return {"current_year": cy, "monthly": monthly}


@pytest.fixture
def origin_dataset(db_session):
    """国别数据集：(CY-1, 1) 自主 60 / 德系 25 / 日系 15；(CY-1, 2) 自主 70 / 德系 30。"""
    cy = datetime.now().year
    rows = [
        (cy - 1, 1, "自主", 60.0),
        (cy - 1, 1, "德系", 25.0),
        (cy - 1, 1, "日系", 15.0),
        (cy - 1, 2, "自主", 70.0),
        (cy - 1, 2, "德系", 30.0),
    ]
    for year, month, origin, sales in rows:
        add_origin_share(db_session, year=year, month=month, origin=origin, sales_volume=sales)
    db_session.commit()
    return {"current_year": cy, "rows": rows}
