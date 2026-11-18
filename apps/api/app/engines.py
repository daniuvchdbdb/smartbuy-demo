from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from statistics import median


class ShoppingIntentParser:
    """Deterministic MVP parser. An AI provider may enrich, never replace, these constraints."""

    CATEGORY_TERMS = {
        "laptops": ("笔记本", "电脑", "游戏本", "编程"),
        "phones": ("手机",),
        "monitors": ("显示器", "屏幕"),
        "headphones": ("耳机",),
        "tablets": ("平板",),
        "accessories": ("充电器", "扩展坞", "键盘", "鼠标", "硬盘"),
    }

    def parse(self, text: str) -> dict:
        category = next(
            (slug for slug, terms in self.CATEGORY_TERMS.items() if any(term in text for term in terms)),
            "laptops",
        )
        budget_match = re.search(r"(?:预算|不超过|以内)\s*[¥￥]?\s*(\d{3,6})", text)
        budget = int(budget_match.group(1)) if budget_match else None
        usage = [label for term, label in (("编程", "programming"), ("游戏", "gaming"), ("办公", "office"), ("设计", "design"), ("剪辑", "video")) if term in text]
        priorities = {
            "performance": 1.0 if any(x in text for x in ("游戏", "性能", "编程")) else 0.6,
            "portability": 0.9 if any(x in text for x in ("轻", "便携", "不重")) else 0.5,
            "battery": 0.9 if any(x in text for x in ("续航", "电池")) else 0.5,
        }
        requirements: dict[str, str | int] = {}
        if re.search(r"(?:1\s*TB|1T|一\s*TB)", text, re.I):
            requirements["storage_gb"] = 1024
        ram = re.search(r"(16|24|32|64)\s*G(?:B)?\s*(?:内存)?", text, re.I)
        if ram:
            requirements["ram_gb"] = int(ram.group(1))
        avoid = ["heavy"] if any(x in text for x in ("不要太重", "不想太重", "轻一点")) else []
        return {"category": category, "budget_max": budget, "usage": usage, "priorities": priorities, "requirements": requirements, "avoid": avoid}


class ScoringEngine:
    @staticmethod
    def fit_score(variant, intent: dict, specs: dict) -> float:
        weights = intent.get("priorities") or {}
        dimensions = {
            "performance": variant.performance_score,
            "portability": variant.portability_score,
            "battery": variant.battery_score,
        }
        weighted = sum(dimensions[k] * float(weights.get(k, 0.5)) for k in dimensions)
        weight_sum = sum(float(weights.get(k, 0.5)) for k in dimensions) or 1
        score = weighted / weight_sum
        requirements = intent.get("requirements") or {}
        for key, required in requirements.items():
            actual = specs.get(key)
            if actual is None or float(actual) < float(required):
                score -= 25
        if "heavy" in (intent.get("avoid") or []) and float(specs.get("weight_kg", 0)) > 2.2:
            score -= 12
        return round(max(0, min(100, score)), 1)

    @staticmethod
    def price_score(current: float, history: list[float]) -> float:
        if len(history) < 2:
            return 50.0
        low, high = min(history), max(history)
        if high == low:
            return 75.0
        return round(max(0, min(100, 100 * (high - current) / (high - low))), 1)

    @staticmethod
    def value_score(fit: float, price_score: float, risk: float) -> float:
        return round(max(0, min(100, fit * 0.58 + price_score * 0.32 + (100 - risk) * 0.10)), 1)

    @staticmethod
    def final_score(fit: float, value: float, price: float, risk: float) -> float:
        return round(fit * 0.5 + value * 0.25 + price * 0.2 - risk * 0.05, 1)


class BuyTimingEngine:
    @staticmethod
    def analyze(current: float, history: list[float]) -> dict:
        if len(history) < 3:
            return {"code": "INSUFFICIENT_DATA", "label": "数据不足", "reason": "价格历史数据不足", "target_price": None}
        low = min(history)
        typical = median(history)
        ratio = (current - low) / low if low else 0
        if ratio <= 0.035:
            label, code = "可以买", "BUY"
            reason = f"当前价接近历史低位 ¥{low:.0f}"
        elif ratio >= 0.10:
            label, code = "建议等等", "WAIT"
            reason = f"当前价比历史低位高 {ratio:.0%}"
        else:
            label, code = "价格一般", "NEUTRAL"
            reason = f"当前价位于近期常见区间，历史中位价 ¥{typical:.0f}"
        return {"code": code, "label": label, "reason": reason, "target_price": round(low, 2)}


@dataclass
class Discount:
    label: str
    amount: float
    verified: bool = True


class EffectivePriceEngine:
    @staticmethod
    def calculate(listed_price: float, discounts: list[Discount], shipping: float = 0) -> dict:
        verified_total = sum(item.amount for item in discounts if item.verified)
        possible_total = sum(item.amount for item in discounts)
        return {
            "effective_price": round(listed_price - verified_total + shipping, 2),
            "possible_effective_price": round(listed_price - possible_total + shipping, 2),
            "confidence": "HIGH" if verified_total == possible_total else "MEDIUM",
            "breakdown": [item.__dict__ for item in discounts] + ([{"label": "运费", "amount": shipping, "verified": True}] if shipping else []),
        }


class ProductMatchingEngine:
    @staticmethod
    def match(raw_title: str, candidates: list[dict]) -> dict:
        normalized = re.sub(r"[^a-z0-9]+", "", raw_title.lower())
        ranked = []
        for candidate in candidates:
            target = re.sub(r"[^a-z0-9]+", "", (candidate["brand"] + candidate["model"] + candidate["title"]).lower())
            similarity = SequenceMatcher(None, normalized, target).ratio()
            features = [token for token in (candidate.get("sku"), candidate.get("model")) if token and token.lower() in raw_title.lower()]
            confidence = min(1.0, similarity * 0.75 + len(features) * 0.2)
            ranked.append((confidence, candidate, features))
        confidence, candidate, features = max(ranked, default=(0, None, []), key=lambda row: row[0])
        status = "MATCHED" if confidence >= 0.85 else "POSSIBLE_MATCH" if confidence >= 0.65 else "MANUAL_REVIEW" if confidence >= 0.4 else "NOT_MATCHED"
        return {"canonical_product_id": candidate.get("id") if candidate else None, "confidence": round(confidence, 3), "matching_features": features, "conflicts": [], "status": status}


class CompatibilityEngine:
    @staticmethod
    def evaluate(required: dict, offered: dict) -> dict:
        conflicts = [key for key, value in required.items() if offered.get(key) != value]
        return {"compatible": not conflicts, "status": "兼容" if not conflicts else "不兼容", "conflicts": conflicts}

