import { useMutation } from '@tanstack/react-query';
import { router, useLocalSearchParams } from 'expo-router';
import { useEffect } from 'react';
import { ActivityIndicator, Pressable, ScrollView, Text, View } from 'react-native';
import { api, Product } from '../lib/api';
import { useRecommendationStore } from '../store';
import { Button, Card, colors, Score, styles, Tag } from '../components/ui';

export default function RecommendationsScreen() {
  const { intentId } = useLocalSearchParams<{ intentId: string }>();
  const setItems = useRecommendationStore((state) => state.setItems);
  const mutation = useMutation({ mutationFn: () => api<{ results: Product[] }>(`/shopping-intents/${intentId}/recommend`, { method: 'POST' }), onSuccess: (data) => setItems(data.results) });
  useEffect(() => { if (intentId) mutation.mutate(); }, [intentId]);
  if (mutation.isPending) return <View style={[styles.screen, { justifyContent: 'center' }]}><ActivityIndicator color={colors.green} /><Text style={{ textAlign: 'center', marginTop: 12 }}>正在计算适合度与价格位置…</Text></View>;
  if (mutation.isError) return <ScrollView contentContainerStyle={styles.content}><Card><Text style={styles.h2}>推荐失败</Text><Text style={styles.muted}>{mutation.error.message}</Text><Button title="重试" onPress={() => mutation.mutate()} /></Card></ScrollView>;
  const items = mutation.data?.results ?? [];
  return <ScrollView contentContainerStyle={styles.content}><Text style={styles.eyebrow}>TOP 3 · 演示数据</Text><Text style={styles.h1}>与你更匹配的选择</Text>{items.map((item, index) => <Pressable key={item.id} onPress={() => router.push(`/product/${item.id}`)}><Card><View style={styles.row}><Tag>#{index + 1}</Tag><Text style={{ color: colors.green, fontWeight: '800' }}>{item.buy_advice.label}</Text></View><Text style={styles.h2}>{item.name}</Text><Text style={styles.muted}>{item.variant}</Text><View style={styles.row}><Score value={item.fit_score} label="适合度" /><Score value={item.value_score} label="性价比" /><Score value={item.price_score} label="价格分" /><View><Text style={{ fontSize: 24, fontWeight: '900' }}>¥{item.current_price}</Text><Text style={styles.caption}>当前价</Text></View></View><Text style={styles.body}>{item.why}</Text></Card></Pressable>)}{items.length >= 2 && <Button title="对比前两款" secondary onPress={() => router.push({ pathname: '/compare', params: { ids: `${items[0].id},${items[1].id}` } })} />}</ScrollView>;
}
