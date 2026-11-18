# 价格引擎

EffectivePriceEngine 分离“已验证优惠”和“可能适用优惠”。稳定到手价只扣除已验证项；可能到手价另行返回，并降低置信度。PriceScore 根据当前价在已观测区间的位置确定。BuyTimingEngine 在至少 3 个价格点后才给出买/等判断，否则返回“数据不足”。

MockPriceProvider 和 ManualPriceProvider 均实现统一的 PriceProvider 接口。首版未接入淘宝、京东、拼多多受保护端点，也不执行验证码、登录或反爬绕过。

