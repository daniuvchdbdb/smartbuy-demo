from types import SimpleNamespace

from app.engines import BuyTimingEngine, CompatibilityEngine, Discount, EffectivePriceEngine, ProductMatchingEngine, ScoringEngine, ShoppingIntentParser


def test_intent_parser_extracts_hard_constraints():
    parsed = ShoppingIntentParser().parse("预算7000，主要编程和游戏，希望1TB硬盘，不要太重")
    assert parsed["category"] == "laptops"
    assert parsed["budget_max"] == 7000
    assert parsed["requirements"]["storage_gb"] == 1024
    assert "heavy" in parsed["avoid"]


def test_fit_score_penalizes_missing_requirement_and_weight():
    variant = SimpleNamespace(performance_score=95, portability_score=60, battery_score=70)
    intent = {"priorities": {"performance": 1, "portability": 0.9, "battery": 0.5}, "requirements": {"storage_gb": 1024}, "avoid": ["heavy"]}
    assert ScoringEngine.fit_score(variant, intent, {"storage_gb": 512, "weight_kg": 2.4}) < 60


def test_price_value_and_buy_timing_are_deterministic():
    assert ScoringEngine.price_score(6000, [7000, 6500, 6000]) == 100
    assert 0 <= ScoringEngine.value_score(90, 80, 20) <= 100
    assert BuyTimingEngine.analyze(6000, [7000, 6500, 5900])["code"] == "BUY"


def test_effective_price_keeps_unverified_discount_separate():
    result = EffectivePriceEngine.calculate(6999, [Discount("店铺优惠", 300), Discount("可能适用补贴", 800, False)], 0)
    assert result["effective_price"] == 6699
    assert result["possible_effective_price"] == 5899
    assert result["confidence"] == "MEDIUM"


def test_matching_does_not_silently_merge_low_confidence():
    result = ProductMatchingEngine.match("完全无关标题", [{"id": 1, "brand": "联想", "model": "Y7000P", "title": "RTX 5060", "sku": "LNV-Y7P"}])
    assert result["status"] in {"NOT_MATCHED", "MANUAL_REVIEW"}


def test_compatibility_is_rule_based():
    assert CompatibilityEngine.evaluate({"mount": "Sony E"}, {"mount": "Canon RF"})["compatible"] is False

