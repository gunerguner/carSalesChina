"""analysis_periods 纯逻辑：PeriodKey 与 monthly/yearly 粒度切换。"""

from types import SimpleNamespace

from backend.models.overall import SalesData
from backend.services.analysis_periods import (
    PeriodKey,
    period_columns,
    period_entry,
    period_key,
)


class TestPeriodKey:
    def test_order_by_year_then_month(self):
        assert PeriodKey(2023, 1) < PeriodKey(2023, 2) < PeriodKey(2024, 1) < PeriodKey(2024, 2)

    def test_order_yearly(self):
        assert PeriodKey(2022) < PeriodKey(2023) < PeriodKey(2024)

    def test_frozen(self):
        key = PeriodKey(2024, 5)
        try:
            key.year = 2025
        except AttributeError:
            pass
        else:
            raise AssertionError("PeriodKey 应为 frozen，不允许修改")

    def test_month_defaults_none(self):
        assert PeriodKey(2024).month is None


class TestPeriodColumns:
    def test_monthly_returns_year_and_month(self):
        cols = period_columns(SalesData, "monthly")
        assert cols == (SalesData.year, SalesData.month)

    def test_yearly_returns_year_only(self):
        assert period_columns(SalesData, "yearly") == (SalesData.year,)


class TestPeriodKeyFromRow:
    """period_key 消费的是 db.exec 的 Row 对象（属性访问）。"""

    @staticmethod
    def _row(year: int, month: int) -> SimpleNamespace:
        return SimpleNamespace(year=year, month=month)

    def test_monthly(self):
        assert period_key(self._row(2024, 3), "monthly") == PeriodKey(2024, 3)

    def test_yearly_drops_month(self):
        assert period_key(self._row(2024, 3), "yearly") == PeriodKey(2024, None)


class TestPeriodEntry:
    def test_monthly_entry(self):
        assert period_entry(PeriodKey(2024, 3)) == {"year": 2024, "month": 3}

    def test_yearly_entry(self):
        assert period_entry(PeriodKey(2024)) == {"year": 2024}
