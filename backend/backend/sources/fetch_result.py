"""外部数据源拉取结果：区分接口失败与成功但无数据。"""

from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

T = TypeVar("T")


@dataclass
class SourceFetchResult:
    """records 为标准化后的入库行；ok 表示该源本次无致命/接口错误。"""

    records: list[dict[str, Any]] = field(default_factory=list)
    ok: bool = True
    errors: list[str] = field(default_factory=list)

    def error_summary(self, max_items: int = 5) -> str | None:
        if not self.errors:
            return None
        head = self.errors[:max_items]
        suffix = "…" if len(self.errors) > max_items else ""
        return "; ".join(head) + suffix

    def to_error_map(self, source_name: str, max_items: int = 5) -> dict[str, str | None]:
        return {source_name: self.error_summary(max_items=max_items)}


@dataclass
class HttpJsonResult:
    """HTTP GET + JSON 解析结果；body 与 error 互斥语义。"""

    body: dict | None = None
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None


@dataclass
class SliceResult(Generic[T]):
    """单次切片拉取：data 为业务数据，error 非空即该切片失败。"""

    data: T
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None


@dataclass
class KeyedSliceResult(Generic[T]):
    """带聚合 key 的切片结果（并发按维度合并时使用）。"""

    key: str
    data: T
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None
