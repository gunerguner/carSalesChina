from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import FASTAPI_PORT
from backend.core.csrf import CSRF_HEADER_NAME, CSRFCookieMiddleware
from backend.core.exception_handlers import register_exception_handlers
from backend.core.logging_config import setup_logging

setup_logging()

from backend.core.database import init_db
from backend.routers import market, brand, analysis, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="中国汽车销售数据平台", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", CSRF_HEADER_NAME],
    expose_headers=[],
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
