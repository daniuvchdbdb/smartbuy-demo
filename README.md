# SmartBuy（智购）

面向中国消费者的 AI 辅助购物决策 MVP。它不是聊天套壳：价格、参数、评分和提醒结论均来自结构化数据与确定性引擎；当前商品与价格明确标记为“演示数据”。

## 已实现闭环

注册/登录 → 自然语言需求解析 → 用户确认 → Top 3 推荐与四维评分 → 两款对比 → 商品详情与价格历史 → 购买时机判断 → 目标价 → 演示价格降至目标 → 通知 → 标记已购 → 我的设备与购后监控。

另含：安全密码散列、所有权隔离、审计日志、限流、有效价格引擎、商品匹配引擎、兼容性引擎、Mock/Manual 价格提供者接口、Mock AI 提供者、管理台、Docker、Alembic 与 EAS 配置。

## 目录

```text
LOCAL_PROJECT_PATH
├─ apps
│  ├─ api       FastAPI + SQLAlchemy + 测试
│  ├─ mobile    Expo SDK 57 + Expo Router
│  └─ admin     Next.js 16 + Tailwind CSS
├─ packages     共享类型与校验
├─ data         本地 SQLite 开发库
├─ docker       容器镜像
├─ docs         架构与运行文档
├─ uploads logs backups
└─ docker-compose.yml
```

## 本地运行

### 后端（无需 Docker 的最快方式）

```powershell
cd LOCAL_PROJECT_PATH
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir apps\api --reload
```

打开 `http://127.0.0.1:8000/docs`。默认使用 `LOCAL_PROJECT_PATH`；生产环境通过 `DATABASE_URL` 切到 PostgreSQL。

### 移动 App

```powershell
cd LOCAL_PROJECT_PATH
npm start
```

真机需把 `EXPO_PUBLIC_API_URL` 设为电脑局域网地址，例如 `http://192.168.1.10:8000/api/v1`；Android 模拟器通常使用 `http://10.0.2.2:8000/api/v1`。

### 管理后台

```powershell
cd LOCAL_PROJECT_PATH
npm run dev
```

打开 `http://127.0.0.1:3000`。

### Docker 基础设施/整栈

```powershell
cd LOCAL_PROJECT_PATH
docker compose up --build
```

## 演示账号

- 邮箱：`demo@example.com`
- 密码：`SmartBuy123`

## 演示数据

共 24 个商品型号：5 款笔记本、5 款手机、4 款显示器、4 款耳机、3 款平板与 3 款配件；每款有结构化规格和 5 个历史价格点。数据仅用于商业原型验证，不代表实时市场报价。

## 测试

```powershell
cd LOCAL_PROJECT_PATH
.\.venv\Scripts\python.exe -m pytest
cd apps\mobile
npx tsc --noEmit
cd ..\admin
npm run lint
npm run build
```

## EAS 构建（不会自动发布）

```powershell
cd LOCAL_PROJECT_PATH
npx eas-cli build --profile development --platform android
npx eas-cli build --profile preview --platform android
npx eas-cli build --profile production --platform android
npx eas-cli build --profile development --platform ios
npx eas-cli build --profile production --platform ios
```

更多说明见 [架构](docs/ARCHITECTURE.md)、[移动端](docs/MOBILE.md)、[API](docs/API.md) 与 [部署](docs/DEPLOYMENT.md)。


## Portfolio scope

This is a self-initiated, AI-assisted learning/demo project, not a claim of commercial employment or production deployment. Private databases, credentials, local browser profiles, customer records and generated build output are excluded. Configure your own services and use synthetic data. Payment/provider integrations and deployment require independent review before production use. No new full end-to-end validation is claimed by this publication.
