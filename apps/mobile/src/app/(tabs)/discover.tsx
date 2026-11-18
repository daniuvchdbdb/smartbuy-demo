import { useQuery } from '@tanstack/react-query';
import { router } from 'expo-router';
import { Pressable, ScrollView, Text, TextInput, View } from 'react-native';
import { useState } from 'react';
import { api, Product } from '../../lib/api';
import { Card, styles, Tag } from '../../components/ui';

export default function DiscoverScreen() {
  const [query, setQuery] = useState('');
  const products = useQuery({ queryKey: ['discover', query], queryFn: () => api<{ items: Product[] }>(`/products?limit=24${query ? `&q=${encodeURIComponent(query)}` : ''}`) });
  return <ScrollView contentContainerStyle={styles.content}><Text style={styles.eyebrow}>结构化商品库 · 演示数据</Text><Text style={styles.h1}>发现</Text><TextInput placeholder="搜索商品或型号" value={query} onChangeText={setQuery} style={styles.input} />{products.data?.items.map((item) => <Pressable key={item.id} onPress={() => router.push(`/product/${item.id}`)}><Card><View style={styles.row}><View style={{ flex: 1 }}><Text style={styles.h2}>{item.name}</Text><Text style={styles.muted}>{item.variant}</Text></View><Text style={{ fontSize: 22, fontWeight: '900' }}>¥{item.current_price}</Text></View><Tag tone={item.buy_advice.code === 'WAIT' ? 'orange' : 'green'}>{item.buy_advice.label}</Tag></Card></Pressable>)}</ScrollView>;
}
