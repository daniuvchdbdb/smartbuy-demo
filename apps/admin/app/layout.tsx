import './globals.css';
import type { Metadata } from 'next';
export const metadata: Metadata = { title: 'SmartBuy 管理后台', description: '商品与价格数据质量控制台' };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="zh-CN"><body>{children}</body></html>; }
