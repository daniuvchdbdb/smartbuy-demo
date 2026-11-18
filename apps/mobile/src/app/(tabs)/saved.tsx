import { useQuery } from '@tanstack/react-query';
import { router } from 'expo-router';
import { Pressable, ScrollView, Text } from 'react-native';
import { api, Product } from '../../lib/api';
import { useAuthStore } from '../../store';
import { Button, Card, styles, Tag } from '../../components/ui';

export default function SavedScreen() {
  const token = useAuthStore((s) => s.token);
  const query = useQuery({ queryKey: ['watchlist'], queryFn: () => api<{ items: Product[] }>('/watchlist'), enabled: !!token });
  if (!token) return <ScrollView contentContainerStyle={styles.content}><Button title="登录后查看关注" onPress={() => router.push('/login')} /></ScrollView>;
  return <ScrollView contentContainerStyle={styles.content}><Text style={styles.h1}>我的关注</Text><Text style={styles.muted}>全部 · 降价 · 接近目标价 · 建议购买 · 建议等等</Text>{query.data?.items.length === 0 && <Card><Text style={styles.body}>还没有收藏商品。</Text></Card>}{query.data?.items.map((item) => <Pressable key={item.id} onPress={() => router.push(`/product/${item.id}`)}><Card><Text style={styles.h2}>{item.name}</Text><Text style={styles.muted}>{item.variant}</Text><Text style={{ fontSize: 24, fontWeight: '900' }}>¥{item.current_price}</Text><Tag>{item.buy_advice.label}</Tag></Card></Pressable>)}</ScrollView>;
}
