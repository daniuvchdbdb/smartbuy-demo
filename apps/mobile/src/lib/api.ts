import { useAuthStore } from '../store';

export const API_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://127.0.0.1:8000/api/v1';

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const token = useAuthStore.getState().token;
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}), ...init?.headers },
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '网络请求失败' }));
    throw new Error(error.detail ?? '网络请求失败');
  }
  if (response.status === 204) return undefined as T;
  return response.json();
}

export type Product = {
  id: number; name: string; brand: string; variant: string; current_price: number;
  fit_score: number; value_score: number; price_score: number; risk_score: number; final_score: number;
  buy_advice: { code: string; label: string; reason: string; target_price?: number };
  specs: Record<string, string | number>; why?: string; demo_data: boolean;
};

