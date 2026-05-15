"""外部数据源拉取结果：区分接口失败与成功但无数据。"""

from dataclasses import dataclass, field
from typing import Any


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
