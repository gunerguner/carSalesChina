from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from backend.core.csrf import verify_csrf
from backend.core.deps import DbSession
from backend.services.refresh_orchestrator import refresh_all_stream

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["admin"],
    dependencies=[Depends(verify_csrf)],
)


@router.post("/data/refresh/stream")
def trigger_refresh_stream(db: DbSession):
    return StreamingResponse(
        refresh_all_stream(db),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
