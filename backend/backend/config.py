import os
from dotenv import load_dotenv

load_dotenv()


def _csv_env(name: str, default: list[str]) -> list[str]:
    raw = os.getenv(name)
    if raw is None:
        return default
    return [item.strip() for item in raw.split(",") if item.strip()]


DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "car_sales")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

FASTAPI_PORT = int(os.getenv("FASTAPI_PORT", 8001))

# 留空时管理刷新接口返回 503，避免带着默认可猜密码上线。
ADMIN_REFRESH_PASSWORD = os.getenv("ADMIN_REFRESH_PASSWORD", "")

# 默认 * 时 main.py 会关闭 allow_credentials。跨域且要带 Cookie 时改成具体源。
CORS_ORIGINS = _csv_env("CORS_ORIGINS", ["*"])
CORS_METHODS = _csv_env("CORS_METHODS", ["*"])
CORS_HEADERS = _csv_env("CORS_HEADERS", ["*"])
