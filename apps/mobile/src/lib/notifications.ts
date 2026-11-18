import * as Device from 'expo-device';
import * as Notifications from 'expo-notifications';

Notifications.setNotificationHandler({ handleNotification: async () => ({ shouldShowBanner: true, shouldShowList: true, shouldPlaySound: true, shouldSetBadge: false }) });

export async function registerForPushNotifications() {
  if (!Device.isDevice) return null;
  const current = await Notifications.getPermissionsAsync();
  const permission = current.status === 'granted' ? current : await Notifications.requestPermissionsAsync();
  if (permission.status !== 'granted') return null;
  return (await Notifications.getExpoPushTokenAsync()).data;
}

export async function showPriceNotification(title: string, body: string) {
  await Notifications.scheduleNotificationAsync({ content: { title, body, data: { type: 'TARGET_PRICE' } }, trigger: null });
}

