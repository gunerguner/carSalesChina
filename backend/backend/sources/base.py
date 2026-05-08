from abc import ABC, abstractmethod
from typing import Any


class BaseDataSource(ABC):
    @abstractmethod
    def get_monthly_overall(self, date: str = None) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def get_brand_ranking(self, date: str = None) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def get_energy_breakdown(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def get_segment_data(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def get_factory_ranking(self, date: str = None) -> list[dict[str, Any]]:
        pass