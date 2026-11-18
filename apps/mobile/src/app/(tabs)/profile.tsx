import { useMutation } from '@tanstack/react-query';
import { router } from 'expo-router';
import { Alert, ScrollView, Text } from 'react-native';
import { api } from '../../lib/api';
import { useAuthStore } from '../../store';
import { Button, Card, styles, Tag } from '../../components/ui';

export default function ProfileScreen() {
  const { token, setToken } = useAuthStore();
  const remove = useMutation({ mutationFn: () => api('/me', { method: 'DELETE' }), onSuccess: async () => { await setToken(null); Alert.alert('账号已删除'); } });
  const confirmDelete = () => Alert.alert('删除账号？', '购物需求、收藏、设备与通知将永久删除。', [{ text: '取消', style: 'cancel' }, { text: '确认删除', style: 'destructive', onPress: () => remove.mutate() }]);
  return <ScrollView contentContainerStyle={styles.content}><Text style={styles.h1}>我的</Text>{!token ? <Card><Text style={styles.h2}>登录后管理个人购物资产</Text><Button title="去登录" onPress={() => router.push('/login')} /></Card> : <><Card><Tag>隐私数据仅自己可见</Tag><Text style={styles.h2}>演示用户</Text><Text style={styles.muted}>订单、设备、偏好与提醒均按用户隔离。</Text></Card><Button title="我的设备" secondary onPress={() => router.push('/devices')} /><Button title="通知中心" secondary onPress={() => router.push('/notifications')} /><Button title="退出登录" secondary onPress={() => setToken(null)} /><Button title="删除账号" secondary onPress={confirmDelete} /></>}</ScrollView>;
}
