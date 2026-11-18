import { useQuery } from '@tanstack/react-query';
import { router } from 'expo-router';
import { ScrollView, Text } from 'react-native';
import { api, Product } from '../lib/api';
import { useAuthStore } from '../store';
import { Button, Card, styles, Tag } from '../components/ui';

type Owned = { id: number; product: Product; purchase_price: number; purchase_date: string; post_purchase_monitoring: boolean };
export default function DevicesScreen() { const token = useAuthStore((s) => s.token); const query = useQuery({ queryKey: ['owned'], queryFn: () => api<{ items: Owned[] }>('/owned-products'), enabled: !!token }); if (!token) return <ScrollView contentContainerStyle={styles.content}><Button title="登录后查看设备" onPress={() => router.push('/login')} /></ScrollView>; return <ScrollView contentContainerStyle={styles.content}><Text style={styles.h1}>我的设备</Text><Text style={styles.muted}>你的个人产品图谱与购后跟踪入口。</Text>{query.data?.items.length === 0 && <Card><Text style={styles.body}>还没有设备。可以从商品详情标记“已购买”。</Text></Card>}{query.data?.items.map((item) => <Card key={item.id}><Tag>购后监控中</Tag><Text style={styles.h2}>{item.product.name}</Text><Text style={styles.muted}>购买价 ¥{item.purchase_price} · {item.purchase_date}</Text><Text style={styles.body}>当前演示价 ¥{item.product.current_price}</Text></Card>)}</ScrollView>; }

