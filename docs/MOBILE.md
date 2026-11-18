# 移动端

Expo SDK 57、React Native 0.86、TypeScript、Expo Router、TanStack Query、Zustand、React Hook Form 与 Zod。认证令牌使用 Expo SecureStore。通知、相册、文件、剪贴板和分享均采用原生能力与权限感知交互。

底部原生导航为“首页 / 发现 / + / 收藏 / 我的”。当前核心路由：`/`、`/login`、`/intent`、`/recommendations`、`/compare`、`/product/[id]`、`/saved`、`/devices`、`/notifications`、`/add`。订单 OCR 只允许选图并明确标注“即将支持”，不会伪造识别或自动保存。

网络失败时首页会明确显示离线提示。当前 React Query 提供会话内缓存；跨进程持久离线缓存列为下一阶段工作。
