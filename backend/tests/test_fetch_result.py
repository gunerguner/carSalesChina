"""sources.fetch_result：结果封装与错误摘要。"""

from backend.sources.fetch_result import (
    HttpJsonResult,
    KeyedSliceResult,
    SliceResult,
    SourceFetchResult,
)


class TestHttpJsonResult:
    def test_ok_when_error_is_none(self):
        assert HttpJsonResult(body={"status": 1}).ok is True

    def test_not_ok_when_error_set(self):
        assert HttpJsonResult(error="timeout").ok is False


class TestSliceResult:
    def test_ok_when_error_is_none(self):
        assert SliceResult(data=[]).ok is True

    def test_not_ok_when_error_set(self):
        assert SliceResult(data=[], error="boom").ok is False


class TestKeyedSliceResult:
    def test_ok_property(self):
        assert KeyedSliceResult(key="retail", data=[]).ok is True
        assert KeyedSliceResult(key="retail", data=[], error="x").ok is False


class TestSourceFetchResult:
    def test_error_summary_none_when_empty(self):
        assert SourceFetchResult().error_summary() is None

    def test_error_summary_joins_and_truncates(self):
        result = SourceFetchResult(errors=[f"e{i}" for i in range(7)])
        summary = result.error_summary(max_items=5)
        assert summary is not None
        assert summary.startswith("e0; e1")
        assert summary.endswith("…")
        assert "e5" not in summary

    def test_to_error_map(self):
        result = SourceFetchResult(errors=["timeout"])
        assert result.to_error_map("yiche") == {"yiche": "timeout"}
