import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { useState } from 'react';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import 'react-native-reanimated';

export default function RootLayout() {
  const [queryClient] = useState(() => new QueryClient({ defaultOptions: { queries: { staleTime: 30_000, retry: 1 } } }));
  return (
    <SafeAreaProvider>
      <QueryClientProvider client={queryClient}>
        <Stack screenOptions={{ headerTintColor: '#13261e', headerBackButtonDisplayMode: 'minimal', contentStyle: { backgroundColor: '#f5f7f4' } }}>
          <Stack.Screen name="index" options={{ headerShown: false }} />
          <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
          <Stack.Screen name="login" options={{ title: '登录' }} />
          <Stack.Screen name="intent" options={{ title: '帮我选' }} />
          <Stack.Screen name="recommendations" options={{ title: '推荐结果' }} />
          <Stack.Screen name="compare" options={{ title: '商品对比' }} />
          <Stack.Screen name="product/[id]" options={{ title: '商品详情' }} />
          <Stack.Screen name="devices" options={{ title: '我的设备' }} />
          <Stack.Screen name="notifications" options={{ title: '通知' }} />
          <Stack.Screen name="add" options={{ presentation: 'modal', title: '添加商品' }} />
        </Stack>
        <StatusBar style="dark" />
      </QueryClientProvider>
    </SafeAreaProvider>
  );
}
