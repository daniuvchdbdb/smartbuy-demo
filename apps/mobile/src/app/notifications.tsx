import { useQuery } from '@tanstack/react-query';
import { router } from 'expo-router';
import { ScrollView, Text } from 'react-native';
import { api } from '../lib/api';
import { useAuthStore } from '../store';
import { Button, Card, styles, Tag } from '../components/ui';

type Notice = { id: number; type: string; title: string; body: string; created_at: string };
export default function NotificationsScreen() { const token = useAuthStore((s) => s.token); const query = useQuery({ queryKey: ['notifications'], queryFn: () => api<{ items: Notice[] }>('/notifications'), enabled: !!token, refetchInterval: 15000 }); if (!token) return <ScrollView contentContainerStyle={styles.content}><Button title="登录后查看通知" onPress={() => router.push('/login')} /></ScrollView>; return <ScrollView contentContainerStyle={styles.content}><Text style={styles.h1}>通知</Text>{query.data?.items.length === 0 && <Card><Text style={styles.body}>暂无通知。</Text></Card>}{query.data?.items.map((item) => <Card key={item.id}><Tag>{item.type}</Tag><Text style={styles.h2}>{item.title}</Text><Text style={styles.body}>{item.body}</Text><Text style={styles.caption}>{new Date(item.created_at).toLocaleString()}</Text></Card>)}</ScrollView>; }

