import { useQuery } from '@tanstack/react-query';
import { useLocalSearchParams } from 'expo-router';
import { ScrollView, Text, View } from 'react-native';
import { api, Product } from '../lib/api';
import { Card, Score, styles, Tag } from '../components/ui';

type Comparison = { items: Product[]; differences: { dimension: string; best_variant_id: number; values: Record<string, number> }[]; summary: string };
export default function CompareScreen() {
  const { ids } = useLocalSearchParams<{ ids: string }>(); const parts = (ids ?? '').split(',').map(Number);
  const query = useQuery({ queryKey: ['compare', ids], queryFn: () => api<Comparison>(`/compare?${parts.map((id) => `variant_ids=${id}`).join('&')}`), enabled: parts.length >= 2 });
  if (!query.data) return <View style={styles.content}><Text>{query.isError ? '对比加载失败' : '正在比较…'}</Text></View>;
  return <ScrollView contentContainerStyle={styles.content}><Text style={styles.eyebrow}>差异引擎 · 演示数据</Text><Text style={styles.h1}>不只是一张参数表</Text><Card><Text style={styles.body}>{query.data.summary}</Text></Card>{query.data.items.map((item) => <Card key={item.id}><View style={styles.row}><Text style={styles.h2}>{item.name}</Text><Tag>{item.buy_advice.label}</Tag></View><Text style={styles.muted}>{item.variant}</Text><View style={styles.row}><Score value={item.fit_score} label="适合度" /><Score value={item.value_score} label="性价比" /><Score value={item.price_score} label="价格" /><View><Text style={{ fontSize: 22, fontWeight: '900' }}>¥{item.current_price}</Text><Text style={styles.caption}>当前价</Text></View></View></Card>)}<Card><Text style={styles.h2}>关键差异</Text>{query.data.differences.map((difference) => <Text key={difference.dimension} style={styles.body}>• {difference.dimension}：商品 #{difference.best_variant_id} 更优</Text>)}</Card></ScrollView>;
}

