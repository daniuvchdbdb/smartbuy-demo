import * as SecureStore from 'expo-secure-store';
import { create } from 'zustand';
import type { Product } from './lib/api';

type AuthState = { token: string | null; hydrated: boolean; setToken: (token: string | null) => Promise<void>; hydrate: () => Promise<void> };
export const useAuthStore = create<AuthState>((set) => ({
  token: null, hydrated: false,
  setToken: async (token) => { if (token) await SecureStore.setItemAsync('smartbuy_token', token); else await SecureStore.deleteItemAsync('smartbuy_token'); set({ token }); },
  hydrate: async () => set({ token: await SecureStore.getItemAsync('smartbuy_token'), hydrated: true }),
}));

type RecommendationState = { items: Product[]; setItems: (items: Product[]) => void };
export const useRecommendationStore = create<RecommendationState>((set) => ({ items: [], setItems: (items) => set({ items }) }));

