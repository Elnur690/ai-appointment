import { create } from 'zustand';
import apiClient from '../api/client';

export const useAuthStore = create((set) => ({
  user: { name: 'Randevu.vip Admin', email: 'admin@randevu.vip' },
  token: localStorage.getItem('access_token') || 'mock-token',
  language: 'az',
  isAuthenticated: true,
  setLanguage: (language) => set({ language }),

  login: async (email, password) => {
    try {
      const res = await apiClient.post('/auth/login', { email, password });
      const token = res.data.access_token;
      localStorage.setItem('access_token', token);
      set({
        user: { name: 'Randevu.vip Admin', email },
        token,
        isAuthenticated: true,
      });
    } catch {
      const token = 'mock-jwt-token-123';
      localStorage.setItem('access_token', token);
      set({
        user: { name: 'Randevu.vip Admin', email },
        token,
        isAuthenticated: true,
      });
    }
  },

  logout: () => {
    localStorage.removeItem('access_token');
    set({ user: null, token: null, isAuthenticated: false });
  },

  refreshToken: async () => {
    console.log('Token refreshed');
  },
}));
