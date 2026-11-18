import { useQuery } from '@tanstack/react-query';
import { Link, router } from 'expo-router';
import { useEffect } from 'react';
import { ActivityIndicator, Pressable, ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { api, Product } from '../../lib/api';
import { useAuthStore } from '../../store';
import { Button, Card, colors, styles, Tag } from '../../components/ui';

export default function HomeScreen() {
  const { token, hydrated, hydrate } = useAuthStore();
  useEffect(() => { hydrate(); }, [hydrate]);
  const products = useQuery({ queryKey: ['home-products'], queryFn: () => api<{ items: Product[] }>('/products?limit=4') });
  if (!hydrated) return <View style={[styles.screen, { justifyContent: 'center' }]}><ActivityIndicator color={colors.green} /></View>;
  return <SafeAreaView style={styles.screen}><ScrollView contentContainerStyle={styles.content}>
    <View style={styles.row}><View><Text style={styles.eyebrow}>SMARTBUY · 演示数据</Text><Text style={styles.h1}>今天想买什么？</Text></View><Pressable onPress={() => router.push('/notifications')}><Text style={{ fontSize: 24 }}>🔔</Text></Pressable></View>
    {!token && <Card><Text style={styles.h2}>先登录，保存你的决策</Text><Text style={styles.muted}>演示账号已准备好，也可以注册自己的账号。</Text><Button title="登录演示账号" onPress={() => router.push('/login')} /></Card>}
    <Pressable onPress={() => router.push('/intent')}><Card><Tag>核心决策入口</Tag><Text style={styles.h2}>帮我选</Text><Text style={styles.body}>描述预算、用途与在意的点，我们会提取成结构化需求。</Text><Text style={{ color: colors.green, fontWeight: '800' }}>开始描述 →</Text></Card></Pressable>
    <View style={styles.row}><Text style={styles.h2}>我的关注</Text><Link href="/(tabs)/saved" style={{ color: colors.green }}>查看全部</Link></View>
    {products.isLoading && <ActivityIndicator color={colors.green} />}
    {products.isError && <Card><Text style={styles.h2}>当前为离线状态</Text><Text style={styles.muted}>无法连接 API，价格可能不是最新状态。请确认后端已启动。</Text></Card>}
    {products.data?.items.slice(0, 2).map((item) => <Pressable key={item.id} onPress={() => router.push(`/product/${item.id}`)}><Card><View style={styles.row}><View style={{ flex: 1 }}><Text style={styles.h2}>{item.name}</Text><Text style={styles.muted}>{item.variant}</Text></View><Text style={{ fontSize: 24, fontWeight: '900', color: colors.ink }}>¥{item.current_price}</Text></View><View style={styles.row}><Tag tone={item.buy_advice.code === 'WAIT' ? 'orange' : 'green'}>{item.buy_advice.label}</Tag><Text style={styles.caption}>适合度 {Math.round(item.fit_score)} · 价格分 {Math.round(item.price_score)}</Text></View></Card></Pressable>)}
  </ScrollView></SafeAreaView>;
}
