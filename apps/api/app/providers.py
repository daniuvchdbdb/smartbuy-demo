from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PriceResult:
    provider: str
    platform: str
    product_id: int
    variant_id: int
    listing_id: str
    seller: str
    listed_price: float
    coupon_price: float | None
    promotion_price: float | None
    effective_price: float
    shipping: float
    timestamp: datetime
    url: str
    confidence: float


class PriceProvider(ABC):
    @abstractmethod
    def get_product_price(self, variant_id: int) -> PriceResult | None: ...

    @abstractmethod
    def search_product(self, query: str) -> list[PriceResult]: ...

    @abstractmethod
    def get_availability(self, variant_id: int) -> bool: ...


class MockPriceProvider(PriceProvider):
    """Returns only explicitly seeded demonstration data."""

    def __init__(self, rows: dict[int, PriceResult] | None = None):
        self.rows = rows or {}

    def get_product_price(self, variant_id: int) -> PriceResult | None:
        return self.rows.get(variant_id)

    def search_product(self, query: str) -> list[PriceResult]:
        return [row for row in self.rows.values() if query.lower() in row.seller.lower()]

    def get_availability(self, variant_id: int) -> bool:
        return variant_id in self.rows


class ManualPriceProvider(MockPriceProvider):
    def submit(self, result: PriceResult) -> None:
        self.rows[result.variant_id] = result


class AIProvider(ABC):
    @abstractmethod
    def explain(self, facts: dict) -> str: ...


class MockAIProvider(AIProvider):
    def explain(self, facts: dict) -> str:
        return facts.get("reason", "基于已验证的结构化参数生成解释。")

