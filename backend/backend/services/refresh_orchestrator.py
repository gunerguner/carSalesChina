"""数据刷新编排：SSE 流式。"""

import logging
from collections.abc import Callable, Iterator

from sqlmodel import Session

from backend.core.progress import ProgressReporter, SSEBridge
from backend.services.import_service import (
    refresh_brand_meta,
    refresh_origin_data,
    refresh_sales_data,
)

logger = logging.getLogger(__name__)


def _to_phase_result(key: str, result: dict) -> dict:
    if key == "brand_meta":
        imported = result.get("inserted", 0) + result.get("updated", 0)
        return {
            "status": result.get("status", "success"),
            "imported": imported,
            "total": max(result.get("total", imported), 1),
        }
    if key == "sales":
        records_count = result.get("records_count", 0)
        return {
            "status": result.get("status", "success"),
            "imported": records_count,
            "total": max(records_count, 1),
            "source_errors": result.get("source_errors"),
        }
    if key == "origin":
        origin_count = result.get("origin_count", 0)
        return {
            "status": result.get("status", "success"),
            "imported": origin_count,
            "total": max(origin_count, 1),
            "source_errors": result.get("source_errors"),
        }
    return result


def aggregate_refresh_status(*statuses: str) -> str:
    normalized = [status for status in statuses if status != "skipped"]
    if not normalized:
        return "success"
    if all(status == "success" for status in normalized):
        return "success"
    if all(status == "failed" for status in normalized):
        return "failed"
    return "partial_failure"


def _stream_run_phase(
    db: Session,
    key: str,
    fn: Callable[[Session], dict],
    reporter: ProgressReporter,
    bridge: SSEBridge,
) -> Iterator[str]:
    reporter.phase_start(key)
    yield from bridge.drain()
    result = fn(db)
    reporter.phase_done(key, _to_phase_result(key, result))
    yield from bridge.drain()
    return result


def refresh_all_stream(db: Session) -> Iterator[str]:
    bridge = SSEBridge()
    reporter = ProgressReporter(bridge.emit)

    try:
        brand_meta_result = yield from _stream_run_phase(
            db, "brand_meta", refresh_brand_meta, reporter, bridge
        )
        sales_result = yield from _stream_sales_phase(db, reporter, bridge)
        origin_result = yield from _stream_run_phase(
            db, "origin", refresh_origin_data, reporter, bridge
        )

        result = {
            "brand_meta": {**brand_meta_result, **_to_phase_result("brand_meta", brand_meta_result)},
            "sales": {**sales_result, **_to_phase_result("sales", sales_result)},
            "origin": {**origin_result, **_to_phase_result("origin", origin_result)},
            "status": aggregate_refresh_status(
                brand_meta_result.get("status", "success"),
                sales_result.get("status", "success"),
                origin_result.get("status", "success"),
            ),
        }
        reporter.done(result)
        yield from bridge.drain()
    except Exception as exc:
        logger.exception("流式刷新失败")
        reporter.error(str(exc))
        yield from bridge.drain()


def _stream_sales_phase(
    db: Session,
    reporter: ProgressReporter,
    bridge: SSEBridge,
) -> Iterator[str]:
    reporter.phase_start("sales")
    yield from bridge.drain()

    def on_progress(current: int, total: int) -> None:
        reporter.phase_progress(
            "sales",
            current,
            total,
            detail=f"品牌销量 {current}/{total}",
        )
        if current % 5 == 0:
            reporter.ping()

    result = refresh_sales_data(
        db,
        reporter=reporter,
        on_brand_progress=on_progress,
    )
    reporter.phase_done("sales", _to_phase_result("sales", result))
    yield from bridge.drain()
    return result
