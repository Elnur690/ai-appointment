import { create } from 'zustand';
import apiClient from '../api/client';

const getSavedUser = () => {
  try {
    const raw = localStorage.getItem('admin_user');
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
};

export const useAuthStore = create((set) => ({
  user: getSavedUser(),
  token: localStorage.getItem('access_token') || null,
  language: 'az',
  isAuthenticated: Boolean(localStorage.getItem('access_token')),
  setLanguage: (language) => set({ language }),

  login: async (email, password) => {
    const res = await apiClient.post('/auth/login', { email, password });
    if (res.data.role && res.data.role !== 'saas_owner') {
      throw new Error('Access denied: SaaS Administrator privileges required.');
    }
    const token = res.data.access_token;
    const userObj = {
      name: 'SaaS Administrator',
      email,
      role: res.data.role || 'saas_owner',
    };
    localStorage.setItem('access_token', token);
    localStorage.setItem('admin_user', JSON.stringify(userObj));
    set({
      user: userObj,
      token,
      isAuthenticated: true,
    });
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('admin_user');
    set({ user: null, token: null, isAuthenticated: false });
  },
}));
