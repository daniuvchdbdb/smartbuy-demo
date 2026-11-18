import { Tabs, router } from 'expo-router';
import { Pressable, Text } from 'react-native';
import { colors } from '../../components/ui';

const Icon = ({ value, focused }: { value: string; focused: boolean }) => <Text style={{ fontSize: focused ? 23 : 21, opacity: focused ? 1 : 0.62 }}>{value}</Text>;

export default function TabLayout() {
  return <Tabs screenOptions={{ headerShown: false, tabBarActiveTintColor: colors.green, tabBarInactiveTintColor: colors.muted, tabBarStyle: { height: 66, paddingTop: 6, paddingBottom: 7, borderTopColor: colors.line } }}>
    <Tabs.Screen name="index" options={{ title: '首页', tabBarIcon: ({ focused }) => <Icon value="⌂" focused={focused} /> }} />
    <Tabs.Screen name="discover" options={{ title: '发现', tabBarIcon: ({ focused }) => <Icon value="⌕" focused={focused} /> }} />
    <Tabs.Screen name="add-placeholder" options={{ title: '', tabBarIcon: () => null, tabBarButton: () => <Pressable accessibilityLabel="添加商品" onPress={() => router.push('/add')} style={{ width: 58, height: 58, marginTop: -12, borderRadius: 29, backgroundColor: colors.green, alignItems: 'center', justifyContent: 'center', borderWidth: 4, borderColor: '#fff' }}><Text style={{ color: '#fff', fontSize: 30, lineHeight: 32 }}>＋</Text></Pressable> }} />
    <Tabs.Screen name="saved" options={{ title: '收藏', tabBarIcon: ({ focused }) => <Icon value="♡" focused={focused} /> }} />
    <Tabs.Screen name="profile" options={{ title: '我的', tabBarIcon: ({ focused }) => <Icon value="◉" focused={focused} /> }} />
  </Tabs>;
}
