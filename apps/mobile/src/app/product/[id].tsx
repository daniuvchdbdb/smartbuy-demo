import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { router, useLocalSearchParams } from 'expo-router';
import { useState } from 'react';
import { Alert, ScrollView, Share, Text, TextInput, View } from 'react-native';
import { api, Product } from '../../lib/api';
import { showPriceNotification } from '../../lib/notifications';
import { useAuthStore } from '../../store';
import { Button, Card, colors, Score, styles, Tag } from '../../components/ui';

type Detail = Product & { price_history: { price: number; observed_at: string }[]; price_summary: { current: number; lowest_30d: number; lowest_90d: number; all_time_low: number }; risk_profile: { level: string; score: number; note: string } };
export default function ProductDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>(); const variantId = Number(id); const token = useAuthStore((s) => s.token); const queryClient = useQueryClient();
  const [target, setTarget] = useState('5999'); const [purchasePrice, setPurchasePrice] = useState('5899');
  const detail = useQuery({ queryKey: ['product', variantId], queryFn: () => api<Detail>(`/products/${variantId}`) });
  const favorite = useMutation({ mutationFn: () => api(`/watchlist/${variantId}`, { method: 'POST' }), onSuccess: () => Alert.alert('已收藏', '后续价格变化会显示在“我的关注”。') });
  const alertMutation = useMutation({ mutationFn: () => api('/target-price-alerts', { method: 'POST', body: JSON.stringify({ variant_id: variantId, target_price: Number(target) }) }), onSuccess: () => Alert.alert('目标价已设置', `低于 ¥${target} 时提醒你。`) });
  const simulate = useMutation({ mutationFn: () => api<{ notifications_created: number }>('/demo/price-change', { method: 'POST', body: JSON.stringify({ variant_id: variantId, effective_price: 5899 }) }), onSuccess: async (result) => { await queryClient.invalidateQueries({ queryKey: ['product', variantId] }); if (result.notifications_created) await showPriceNotification('目标价已达到', '你关注的商品演示价格已降至 ¥5899'); Alert.alert('演示价格已更新', `生成 ${result.notifications_created} 条提醒。`); } });
  const purchase = useMutation({ mutationFn: () => api('/owned-products', { method: 'POST', body: JSON.stringify({ variant_id: variantId, purchase_price: Number(purchasePrice), purchase_date: new Date().toISOString().slice(0, 10) }) }), onSuccess: () => { Alert.alert('已加入我的设备', '购后价格监控已继续开启。'); router.push('/devices'); } });
  if (detail.isLoading) return <View style={styles.content}><Text>加载中…</Text></View>; if (!detail.data) return <View style={styles.content}><Text>无法加载商品。</Text></View>; const item = detail.data; const max = Math.max(...item.price_history.map((p) => p.price));
  return <ScrollView contentContainerStyle={styles.content}><Tag>演示数据</Tag><Text style={styles.h1}>{item.name}</Text><Text style={styles.muted}>{item.brand} · {item.variant}</Text><Card><View style={styles.row}><View><Text style={{ fontSize: 34, fontWeight: '900' }}>¥{item.current_price}</Text><Text style={styles.caption}>当前预估到手价</Text></View><View><Tag tone={item.buy_advice.code === 'WAIT' ? 'orange' : 'green'}>{item.buy_advice.label}</Tag></View></View><Text style={styles.body}>{item.buy_advice.reason}</Text></Card>
    <Card><Text style={styles.h2}>为什么适合你</Text><View style={styles.row}><Score value={item.fit_score} label="适合度" /><Score value={item.value_score} label="性价比" /><Score value={item.price_score} label="价格" /><Score value={100 - item.risk_score} label="稳妥度" /></View></Card>
    <Card><Text style={styles.h2}>价格趋势</Text><View style={{ height: 100, flexDirection: 'row', alignItems: 'flex-end', gap: 8 }}>{item.price_history.map((p) => <View key={p.observed_at} accessibilityLabel={`${p.observed_at}，${p.price}元`} style={{ flex: 1, height: `${Math.max(15, p.price / max * 100)}%`, borderRadius: 6, backgroundColor: colors.green }} />)}</View><View style={styles.row}><Text style={styles.caption}>90日低 ¥{item.price_summary.lowest_90d}</Text><Text style={styles.caption}>30日低 ¥{item.price_summary.lowest_30d}</Text></View></Card>
    <Card><Text style={styles.h2}>核心参数</Text>{Object.entries(item.specs).map(([key, value]) => <View key={key} style={styles.row}><Text style={styles.muted}>{key}</Text><Text style={styles.body}>{String(value)}</Text></View>)}</Card>
    <Card><Text style={styles.h2}>常见问题与风险</Text><Text style={styles.body}>风险等级：{item.risk_profile.level}</Text><Text style={styles.muted}>{item.risk_profile.note}</Text></Card>
    {!token ? <Button title="登录后收藏与监控" onPress={() => router.push('/login')} /> : <><Card><Text style={styles.h2}>目标价格</Text><TextInput keyboardType="numeric" value={target} onChangeText={setTarget} style={styles.input} /><Button title="设置降价提醒" onPress={() => alertMutation.mutate()} /><Button title="收藏商品" secondary onPress={() => favorite.mutate()} /></Card><Card><Text style={styles.h2}>完成闭环演示</Text><Text style={styles.muted}>先设置目标价，再把演示价格改为 ¥5899，服务端将生成一条目标价通知。</Text><Button title="模拟降至 ¥5899" secondary onPress={() => simulate.mutate()} /><TextInput keyboardType="numeric" value={purchasePrice} onChangeText={setPurchasePrice} style={styles.input} /><Button title="标记为已购买" onPress={() => purchase.mutate()} /></Card></>}
    <Button title="分享分析卡片" secondary onPress={() => Share.share({ message: `${item.name}\n适合度 ${Math.round(item.fit_score)}\n当前演示价 ¥${item.current_price}\n建议：${item.buy_advice.label}` })} />
  </ScrollView>;
}

