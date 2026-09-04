"""progress 纯逻辑：SSE 帧格式、SSEBridge、ProgressReporter。"""

import json

from backend.services.progress import PHASE_LABELS, ProgressReporter, SSEBridge, format_sse


class TestFormatSse:
    def test_frame_layout(self):
        frame = format_sse("progress", {"phase": "sales"})
        assert frame == 'event: progress\ndata: {"phase": "sales"}\n\n'

    def test_chinese_not_escaped(self):
        frame = format_sse("error", {"message": "品牌元数据"})
        assert "品牌元数据" in frame
        assert "\\u" not in frame

    def test_data_is_valid_json(self):
        frame = format_sse("done", {"status": "success", "n": 1})
        payload = frame.split("data: ", 1)[1].strip()
        assert json.loads(payload) == {"status": "success", "n": 1}


class TestSSEBridge:
    def test_emit_then_drain_in_order(self):
        bridge = SSEBridge()
        bridge.emit("progress", {"n": 1})
        bridge.emit("progress", {"n": 2})
        assert list(bridge.drain()) == [
            format_sse("progress", {"n": 1}),
            format_sse("progress", {"n": 2}),
        ]

    def test_drain_empties_queue(self):
        bridge = SSEBridge()
        bridge.emit("ping", {})
        list(bridge.drain())
        assert list(bridge.drain()) == []

    def test_drain_is_lazy_generator(self):
        bridge = SSEBridge()
        bridge.emit("ping", {})
        gen = bridge.drain()
        bridge.emit("ping", {})  # drain 过程中新增的帧也会被取出
        assert len(list(gen)) == 2


class TestProgressReporter:
    @staticmethod
    def _make() -> tuple[ProgressReporter, list]:
        events: list[tuple[str, dict]] = []
        return ProgressReporter(lambda e, d: events.append((e, d))), events

    def test_phase_start_payload(self):
        reporter, events = self._make()
        reporter.phase_start("sales")
        event, data = events[-1]
        assert event == "progress"
        assert data["phase"] == "sales"
        assert data["label"] == PHASE_LABELS["sales"]
        assert data["status"] == "running"
        assert (data["current"], data["total"]) == (0, 1)

    def test_phase_start_unknown_label_falls_back_to_key(self):
        reporter, events = self._make()
        reporter.phase_start("unknown_phase")
        assert events[-1][1]["label"] == "unknown_phase"

    def test_phase_progress_updates_current_total(self):
        reporter, events = self._make()
        reporter.phase_start("sales")
        reporter.phase_progress("sales", 3, 10, detail="品牌销量 3/10")
        data = events[-1][1]
        assert (data["current"], data["total"]) == (3, 10)
        assert data["detail"] == "品牌销量 3/10"
        assert data["status"] == "running"
        assert data["elapsed"] >= 0

    def test_phase_done_success_marks_done(self):
        reporter, events = self._make()
        reporter.phase_start("origin")
        reporter.phase_done("origin", {"status": "success", "total": 5, "imported": 5})
        data = events[-1][1]
        assert data["status"] == "done"
        assert (data["current"], data["total"]) == (5, 5)

    def test_phase_done_failed_marks_failed(self):
        reporter, events = self._make()
        reporter.phase_done("origin", {"status": "failed", "source_errors": {"origin": "boom"}})
        data = events[-1][1]
        assert data["status"] == "failed"
        assert data["source_errors"] == {"origin": "boom"}

    def test_phase_done_defaults_total_at_least_one(self):
        reporter, events = self._make()
        reporter.phase_done("brand_meta", {})
        data = events[-1][1]
        assert data["total"] == 1
        assert data["imported"] == 0

    def test_error_and_done_and_ping_events(self):
        reporter, events = self._make()
        reporter.error("刷新失败")
        reporter.done({"status": "success"})
        reporter.ping()
        assert [e for e, _ in events] == ["error", "done", "ping"]
        assert events[0][1] == {"message": "刷新失败"}
        assert events[2][1] == {}
