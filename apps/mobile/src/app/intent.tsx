import { useMutation } from '@tanstack/react-query';
import { router } from 'expo-router';
import { useState } from 'react';
import { Alert, ScrollView, Text, TextInput, View } from 'react-native';
import { api } from '../lib/api';
import { useAuthStore } from '../store';
import { Button, Card, styles, Tag } from '../components/ui';

type ParsedIntent = { id: number; budget_max?: number; usage: string[]; priorities: Record<string, number>; requirements: Record<string, number>; avoid: string[]; category: string };
export default function IntentScreen() {
  const token = useAuthStore((state) => state.token);
  const [text, setText] = useState('预算7000，主要编程和游戏，希望1TB硬盘，不要太重');
  const [parsed, setParsed] = useState<ParsedIntent | null>(null);
  const mutation = useMutation({ mutationFn: () => api<ParsedIntent>('/shopping-intents', { method: 'POST', body: JSON.stringify({ text }) }), onSuccess: setParsed, onError: (error) => Alert.alert('无法解析', error.message) });
  if (!token) return <ScrollView contentContainerStyle={styles.content}><Card><Text style={styles.h2}>登录后开始选购</Text><Button title="去登录" onPress={() => router.push('/login')} /></Card></ScrollView>;
  return <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled"><Text style={styles.eyebrow}>把需求说清楚，比先看型号更重要</Text><Text style={styles.h1}>你想买什么？</Text><TextInput multiline value={text} onChangeText={setText} style={[styles.input, { height: 150, textAlignVertical: 'top', paddingTop: 14 }]} /><Button title={mutation.isPending ? '正在提取…' : '提取需求'} disabled={mutation.isPending || text.length < 3} onPress={() => mutation.mutate()} />
    {parsed && <Card><View style={styles.row}><Text style={styles.h2}>请确认识别结果</Text><Tag>可编辑将在下一版加入</Tag></View><Text style={styles.body}>品类：{parsed.category}</Text><Text style={styles.body}>预算上限：¥{parsed.budget_max ?? '未指定'}</Text><Text style={styles.body}>用途：{parsed.usage.join('、') || '通用'}</Text><Text style={styles.body}>硬性要求：{Object.entries(parsed.requirements).map(([k, v]) => `${k} ≥ ${v}`).join('、') || '无'}</Text><Text style={styles.body}>避免：{parsed.avoid.join('、') || '无'}</Text><Button title="确认并查看推荐" onPress={() => router.push({ pathname: '/recommendations', params: { intentId: parsed.id } })} /></Card>}
  </ScrollView>;
}

