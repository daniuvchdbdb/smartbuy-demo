import * as Clipboard from 'expo-clipboard';
import * as ImagePicker from 'expo-image-picker';
import { router } from 'expo-router';
import { Alert, ScrollView, Text } from 'react-native';
import { Button, Card, styles, Tag } from '../components/ui';

export default function AddScreen() { const paste = async () => { const content = await Clipboard.getStringAsync(); if (!content) return Alert.alert('剪贴板为空'); Alert.alert('已读取链接', `${content.slice(0, 100)}\n\n商品链接识别将在接入合规数据源后开放。`); }; const selectOrder = async () => { const permission = await ImagePicker.requestMediaLibraryPermissionsAsync(); if (!permission.granted) return Alert.alert('需要照片权限', '只有你主动选择图片后才会读取。'); await ImagePicker.launchImageLibraryAsync({ mediaTypes: ['images'] }); Alert.alert('即将支持', 'OCR 结果确认流程尚未接入，本次不会保存图片。'); };
  return <ScrollView contentContainerStyle={styles.content}><Text style={styles.h1}>添加商品</Text><Text style={styles.muted}>不会自动保存 OCR 或剪贴板内容。</Text><Card><Text style={styles.h2}>粘贴商品链接</Text><Button title="读取剪贴板" onPress={paste} /></Card><Card><Text style={styles.h2}>搜索商品</Text><Button title="浏览演示商品" secondary onPress={() => router.replace('/')} /></Card><Card><Tag tone="orange">即将支持</Tag><Text style={styles.h2}>扫描订单</Text><Text style={styles.muted}>可选择图片，但识别结果保存功能暂未开放。</Text><Button title="选择订单截图" secondary onPress={selectOrder} /></Card><Card><Tag tone="orange">即将支持</Tag><Text style={styles.h2}>扫描商品页面 / 手动添加</Text><Button title="尚未开放" disabled /></Card></ScrollView>; }
