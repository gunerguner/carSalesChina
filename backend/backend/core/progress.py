"""流式刷新进度上报。"""

import json
import time
from collections.abc import Callable, Iterator
from typing import Any

PHASE_LABELS: dict[str, str] = {
    "brand_meta": "品牌元数据",
    "sales": "销量数据",
    "origin": "国别占比",
}


def format_sse(event: str, data: dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


class SSEBridge:
    """收集 SSE 帧，供同步生成器在步骤间 drain。"""

    def __init__(self) -> None:
        self.frames: list[str] = []

    def emit(self, event_type: str, data: dict[str, Any]) -> None:
        self.frames.append(format_sse(event_type, data))

    def drain(self) -> Iterator[str]:
        while self.frames:
            yield self.frames.pop(0)


class ProgressReporter:
    def __init__(self, emit: Callable[[str, dict[str, Any]], None] | None = None) -> None:
        self._emit = emit or (lambda _event_type, _data: None)
        self._phase_start_times: dict[str, float] = {}

    def phase_start(self, key: str, label: str | None = None) -> None:
        self._phase_start_times[key] = time.perf_counter()
        self._emit(
            "progress",
            {
                "phase": key,
                "label": label or PHASE_LABELS.get(key, key),
                "status": "running",
                "current": 0,
                "total": 1,
                "imported": 0,
                "elapsed": 0.0,
            },
        )

    def phase_progress(
        self,
        key: str,
        current: int,
        total: int,
        detail: str | None = None,
        *,
        imported: int = 0,
    ) -> None:
        start = self._phase_start_times.get(key, time.perf_counter())
        self._emit(
            "progress",
            {
                "phase": key,
                "label": PHASE_LABELS.get(key, key),
                "status": "running",
                "current": current,
                "total": total,
                "imported": imported,
                "detail": detail,
                "elapsed": round(time.perf_counter() - start, 2),
            },
        )

    def phase_done(self, key: str, result: dict[str, Any]) -> None:
        start = self._phase_start_times.get(key, time.perf_counter())
        elapsed = result.get("elapsed", round(time.perf_counter() - start, 2))
        status = result.get("status", "success")
        self._emit(
            "progress",
            {
                "phase": key,
                "label": PHASE_LABELS.get(key, key),
                "status": "failed" if status == "failed" else "done",
                "current": result.get("total", 1),
                "total": max(result.get("total", 1), 1),
                "imported": result.get("imported", 0),
                "source_errors": result.get("source_errors"),
                "elapsed": elapsed,
            },
        )

    def error(self, message: str, phase: str | None = None) -> None:
        payload: dict[str, Any] = {"message": message}
        if phase:
            payload["phase"] = phase
        self._emit("error", payload)

    def done(self, result: dict[str, Any]) -> None:
        self._emit("done", result)

    def ping(self) -> None:
        self._emit("ping", {})
