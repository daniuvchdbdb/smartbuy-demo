# 部署

开发可直接使用 SQLite；联调 PostgreSQL/Redis 使用 `docker compose up --build`。生产环境应设置强密钥、限制 CORS、把上传放在私有对象存储并使用短期签名 URL、把 API/admin 放在 TLS 反向代理后、为 RQ worker 与 scheduler 独立部署，并关闭 `DEMO_MODE`。

移动端使用 `eas.json` 的 development、preview、production 配置。iOS 构建需要 Apple 开发者凭据，Android 生产构建需要 Play 签名配置；仓库不会自动发布。

上线前还需：真实数据提供者授权、平台规则审查、隐私政策/用户协议、推送凭据、备份恢复演练、可观测性和渗透测试。
