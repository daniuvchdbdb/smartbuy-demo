import type { PropsWithChildren } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

export const colors = { ink: '#14231c', muted: '#66736d', green: '#16794b', pale: '#e8f4ed', card: '#ffffff', bg: '#f5f7f4', orange: '#d66a22', line: '#dfe5e1' };
export function Card({ children }: PropsWithChildren) { return <View style={styles.card}>{children}</View>; }
export function Tag({ children, tone = 'green' }: PropsWithChildren<{ tone?: 'green' | 'orange' }>) { return <View style={[styles.tag, tone === 'orange' && styles.tagOrange]}><Text style={[styles.tagText, tone === 'orange' && { color: colors.orange }]}>{children}</Text></View>; }
export function Button({ title, onPress, secondary = false, disabled = false }: { title: string; onPress?: () => void; secondary?: boolean; disabled?: boolean }) { return <Pressable accessibilityRole="button" disabled={disabled} onPress={onPress} style={[styles.button, secondary && styles.buttonSecondary, disabled && { opacity: 0.45 }]}><Text style={[styles.buttonText, secondary && { color: colors.green }]}>{title}</Text></Pressable>; }
export function Score({ value, label }: { value: number; label: string }) { return <View><Text style={styles.score}>{Math.round(value)}</Text><Text style={styles.caption}>{label}</Text></View>; }

export const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.bg }, content: { padding: 18, gap: 14, paddingBottom: 40 },
  eyebrow: { color: colors.green, fontWeight: '700', letterSpacing: 1 }, h1: { color: colors.ink, fontSize: 30, lineHeight: 38, fontWeight: '800' }, h2: { color: colors.ink, fontSize: 20, fontWeight: '800' },
  body: { color: colors.ink, fontSize: 15, lineHeight: 23 }, muted: { color: colors.muted, lineHeight: 20 }, caption: { color: colors.muted, fontSize: 12 },
  card: { backgroundColor: colors.card, borderRadius: 20, padding: 16, gap: 10, borderWidth: 1, borderColor: '#edf0ee' }, row: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 12 },
  button: { minHeight: 50, backgroundColor: colors.green, borderRadius: 15, alignItems: 'center', justifyContent: 'center', paddingHorizontal: 18 }, buttonSecondary: { backgroundColor: colors.pale, borderWidth: 1, borderColor: '#b9dbc8' }, buttonText: { color: 'white', fontWeight: '800', fontSize: 16 },
  tag: { alignSelf: 'flex-start', paddingHorizontal: 9, paddingVertical: 5, borderRadius: 999, backgroundColor: colors.pale }, tagOrange: { backgroundColor: '#fff0e6' }, tagText: { color: colors.green, fontWeight: '700', fontSize: 12 },
  input: { minHeight: 50, borderWidth: 1, borderColor: colors.line, borderRadius: 15, paddingHorizontal: 14, backgroundColor: '#fff', color: colors.ink }, score: { color: colors.green, fontSize: 32, lineHeight: 36, fontWeight: '900' }, divider: { height: 1, backgroundColor: colors.line },
});
