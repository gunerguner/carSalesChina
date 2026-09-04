"""refresh_orchestrator：SSE 流式刷新编排。"""

import json

import pytest

from backend.services import refresh_orchestrator
from backend.services.refresh_orchestrator import (
    _to_phase_result,
    aggregate_refresh_status,
    refresh_all_stream,
)


def parse_frames(frames: list[str]) -> list[tuple[str, dict]]:
    out = []
    for frame in frames:
        lines = frame.strip().split("\n")
        event = lines[0].removeprefix("event: ")
        data = json.loads(lines[1].removeprefix("data: "))
        out.append((event, data))
    return out


class TestAggregateRefreshStatus:
    @pytest.mark.parametrize(
        ("statuses", "expected"),
        [
            (("success", "success"), "success"),
            (("failed", "failed"), "failed"),
            (("success", "failed"), "partial_failure"),
            (("skipped", "skipped"), "success"),
            (("skipped", "success"), "success"),
            (("skipped", "failed"), "failed"),
            (("skipped", "failed", "success"), "partial_failure"),
            ((), "success"),
        ],
    )
    def test_combinations(self, statuses, expected):
        assert aggregate_refresh_status(*statuses) == expected


class TestToPhaseResult:
    def test_brand_meta_sums_inserted_and_updated(self):
        result = _to_phase_result("brand_meta", {"inserted": 2, "updated": 3, "total": 10})
        assert result == {"status": "success", "imported": 5, "total": 10}

    def test_brand_meta_total_at_least_one(self):
        assert _to_phase_result("brand_meta", {"inserted": 0, "updated": 0})["total"] == 1

    def test_sales_uses_records_count(self):
        result = _to_phase_result(
            "sales", {"records_count": 7, "source_errors": {"overall": None}}
        )
        assert result["imported"] == 7
        assert result["total"] == 7
        assert result["source_errors"] == {"overall": None}

    def test_origin_uses_origin_count(self):
        assert _to_phase_result("origin", {"origin_count": 4})["imported"] == 4

    def test_unknown_key_passthrough(self):
        assert _to_phase_result("whatever", {"a": 1}) == {"a": 1}


@pytest.fixture
def patch_phases(monkeypatch):
    """把三个刷新函数替换为可控假实现，返回调用记录。"""

    def install(brand_meta_result=None, sales_result=None, origin_result=None, sales_exc=None):
        calls = []

        def fake_brand_meta(db):
            calls.append("brand_meta")
            if brand_meta_result is None:
                return {"inserted": 1, "updated": 0, "total": 1, "status": "success"}
            return brand_meta_result

        def fake_sales(db, *, reporter=None, on_brand_progress=None):
            calls.append("sales")
            if sales_exc is not None:
                raise sales_exc
            if on_brand_progress is not None:
                on_brand_progress(5, 10)
            if sales_result is None:
                return {"records_count": 5, "status": "success", "source_errors": None}
            return sales_result

        def fake_origin(db):
            calls.append("origin")
            if origin_result is None:
                return {"origin_count": 2, "status": "success"}
            return origin_result

        monkeypatch.setattr(refresh_orchestrator, "refresh_brand_meta", fake_brand_meta)
        monkeypatch.setattr(refresh_orchestrator, "refresh_sales_data", fake_sales)
        monkeypatch.setattr(refresh_orchestrator, "refresh_origin_data", fake_origin)
        return calls

    return install


class TestRefreshAllStream:
    def test_frame_sequence_follows_phase_order(self, db_session, patch_phases):
        calls = patch_phases()
        frames = list(refresh_all_stream(db_session))
        parsed = parse_frames(frames)
        events = [(e, d["phase"], d["status"]) for e, d in parsed if e == "progress"]
        assert events == [
            ("progress", "brand_meta", "running"),
            ("progress", "brand_meta", "done"),
            ("progress", "sales", "running"),
            # fake 的 on_brand_progress(5, 10) 产生一条中间 running 帧（5 % 5 == 0 触发 ping）
            ("progress", "sales", "running"),
            ("progress", "sales", "done"),
            ("progress", "origin", "running"),
            ("progress", "origin", "done"),
        ]
        # 执行顺序有依赖：brand_meta → sales → origin
        assert calls == ["brand_meta", "sales", "origin"]

    def test_sales_progress_frames_and_ping(self, db_session, patch_phases):
        patch_phases()
        parsed = parse_frames(list(refresh_all_stream(db_session)))
        progress_events = [d for e, d in parsed if e == "progress" and d["phase"] == "sales"]
        assert any("品牌销量 5/10" in (p.get("detail") or "") for p in progress_events)
        assert ("ping", {}) in parsed

    def test_done_event_contains_aggregated_result(self, db_session, patch_phases):
        patch_phases(
            brand_meta_result={"inserted": 2, "updated": 1, "total": 3, "status": "success"},
            sales_result={"records_count": 9, "status": "success", "source_errors": None},
            origin_result={"origin_count": 4, "status": "success"},
        )
        parsed = parse_frames(list(refresh_all_stream(db_session)))
        event, done_data = parsed[-1]
        assert event == "done"
        assert done_data["status"] == "success"
        assert done_data["brand_meta"]["imported"] == 3
        assert done_data["sales"]["imported"] == 9
        assert done_data["origin"]["imported"] == 4

    def test_partial_failure_aggregated(self, db_session, patch_phases):
        patch_phases(origin_result={"origin_count": 0, "status": "failed"})
        parsed = parse_frames(list(refresh_all_stream(db_session)))
        assert parsed[-1][1]["status"] == "partial_failure"
        assert parsed[-2][1]["status"] == "failed"  # origin phase_done 标记 failed

    def test_exception_emits_error_event_and_stops(self, db_session, patch_phases):
        patch_phases(sales_exc=RuntimeError("易车接口炸了"))
        frames = list(refresh_all_stream(db_session))
        parsed = parse_frames(frames)
        assert parsed[-1][0] == "error"
        assert "易车接口炸了" in parsed[-1][1]["message"]
        # sales 阶段抛错后 origin 不再执行
        assert all(e != "progress" or d["phase"] != "origin" for e, d in parsed)
