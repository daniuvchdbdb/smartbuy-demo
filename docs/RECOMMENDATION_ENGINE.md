# 推荐引擎

流程：解析 ShoppingIntent → 预算等硬约束 → 规格要求 → FitScore → PriceScore → ValueScore → RiskScore → FinalScore。

FitScore 使用性能、便携和续航维度及用户权重，并对不满足存储/重量等要求确定性扣分。当前公式：`Final = Fit×0.50 + Value×0.25 + Price×0.20 - Risk×0.05`。所有中间分均持久化到 recommendation_results，便于解释与回放。

MockAIProvider 只把结构化事实变成易读说明，不生成价格、规格、历史或分数。

