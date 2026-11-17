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

const getSavedLang = () => {
  try {
    const saved = localStorage.getItem('randevu_lang');
    return saved === 'en' ? 'en' : 'az';
  } catch {
    return 'az';
  }
};

export const useAuthStore = create((set) => ({
  user: getSavedUser(),
  token: localStorage.getItem('access_token') || null,
  language: getSavedLang(),
  isAuthenticated: Boolean(localStorage.getItem('access_token')),
  setLanguage: (language) => {
    const next = language === 'en' ? 'en' : 'az';
    try {
      localStorage.setItem('randevu_lang', next);
    } catch {
      // ignore storage error
    }
    set({ language: next });
  },

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
