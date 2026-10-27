from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import CORS_HEADERS, CORS_METHODS, CORS_ORIGINS, FASTAPI_PORT
from backend.core.csrf import CSRFCookieMiddleware
from backend.routers.exception_handlers import register_exception_handlers
from backend.core.logging_config import setup_logging

setup_logging()

from backend.core.database import init_db
from backend.routers import market, brand, analysis, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="中国汽车销售数据平台", version="1.0.0", lifespan=lifespan)

# * 与 allow_credentials 不能同时成立：通配来源时浏览器会拒绝携带 Cookie。
allow_credentials = "*" not in CORS_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=allow_credentials,
    allow_methods=CORS_METHODS,
    allow_headers=CORS_HEADERS,
)

app.add_middleware(CSRFCookieMiddleware)

app.include_router(market.router)
app.include_router(brand.router)
app.include_router(analysis.router)
app.include_router(admin.router)
register_exception_handlers(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=FASTAPI_PORT, reload=True)
