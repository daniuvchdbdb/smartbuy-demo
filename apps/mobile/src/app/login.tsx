import { zodResolver } from '@hookform/resolvers/zod';
import { router } from 'expo-router';
import { Controller, useForm } from 'react-hook-form';
import { Alert, ScrollView, Text, TextInput } from 'react-native';
import { z } from 'zod';
import { api } from '../lib/api';
import { useAuthStore } from '../store';
import { Button, Card, styles } from '../components/ui';

const schema = z.object({ email: z.string().email('请输入有效邮箱'), password: z.string().min(8, '密码至少 8 位') });
type FormData = z.infer<typeof schema>;

export default function LoginScreen() {
  const setToken = useAuthStore((state) => state.setToken);
  const { control, handleSubmit, formState: { errors, isSubmitting }, setValue } = useForm<FormData>({ resolver: zodResolver(schema), defaultValues: { email: 'demo@example.com', password: 'SmartBuy123' } });
  const submit = async (values: FormData) => { try { const result = await api<{ token: string }>('/auth/login', { method: 'POST', body: JSON.stringify(values) }); await setToken(result.token); router.replace('/'); } catch (error) { Alert.alert('登录失败', error instanceof Error ? error.message : '请稍后重试'); } };
  return <ScrollView contentContainerStyle={styles.content}><Card><Text style={styles.h1}>欢迎回来</Text><Text style={styles.muted}>账号信息会保存在设备安全存储中。</Text>
    <Controller control={control} name="email" render={({ field: { onChange, value } }) => <TextInput autoCapitalize="none" keyboardType="email-address" placeholder="邮箱" style={styles.input} value={value} onChangeText={onChange} />} />{errors.email && <Text style={{ color: '#b42318' }}>{errors.email.message}</Text>}
    <Controller control={control} name="password" render={({ field: { onChange, value } }) => <TextInput secureTextEntry placeholder="密码" style={styles.input} value={value} onChangeText={onChange} />} />{errors.password && <Text style={{ color: '#b42318' }}>{errors.password.message}</Text>}
    <Button title={isSubmitting ? '登录中…' : '登录'} disabled={isSubmitting} onPress={handleSubmit(submit)} /><Button title="填入演示账号" secondary onPress={() => { setValue('email', 'demo@example.com'); setValue('password', 'SmartBuy123'); }} />
  </Card></ScrollView>;
}

