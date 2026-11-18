# 数据库

核心规范化链路：`categories → products → product_variants → product_specs → spec_definitions`。价格使用追加写入的 `price_records`，每条都含来源、观测时间和置信度。

已创建附件要求的用户、产品、匹配、商家/平台、价格、关注/提醒、意图/推荐、评论、兼容、设备关系、订单/权益、通知、联盟归因与审计表。核心闭环使用强类型列；尚未进入 MVP 的扩展域先以独立表保留边界，后续迁移成完整字段。

默认 SQLite 位于 `LOCAL_PROJECT_PATH`。复制 `.env.example` 为 `.env` 并设置 PostgreSQL URL 后使用 Alembic：

```powershell
cd LOCAL_PROJECT_PATH
..\..\.venv\Scripts\alembic.exe upgrade head
```

