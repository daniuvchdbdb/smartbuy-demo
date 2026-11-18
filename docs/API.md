# API

交互文档启动后位于 `/docs`。主要端点：

- `POST /api/v1/auth/register|login`
- `GET /api/v1/products`、`GET /api/v1/products/{variant_id}`
- `POST /api/v1/shopping-intents`
- `POST /api/v1/shopping-intents/{id}/recommend`
- `GET /api/v1/compare?variant_ids=1&variant_ids=2`
- `POST /api/v1/target-price-alerts`
- `POST /api/v1/demo/price-change`
- `GET /api/v1/notifications`
- `POST|GET /api/v1/owned-products`
- `POST /api/v1/tools/effective-price|product-match`

私有资源始终用当前用户 ID 过滤。演示改价接口只在 `DEMO_MODE=true` 可用。

