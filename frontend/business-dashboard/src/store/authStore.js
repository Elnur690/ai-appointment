import { create } from 'zustand';
import api from '../api/client';

const getSavedUser = () => {
  try {
    const raw = localStorage.getItem('business_user');
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
  businessContext: null,
  branches: [],
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

  login: (user) => {
    localStorage.setItem('business_user', JSON.stringify(user));
    set({ user, isAuthenticated: true });
  },

  fetchBusinessProfile: async () => {
    try {
      const [bizRes, branchRes] = await Promise.all([
        api.get('/businesses/'),
        api.get('/branches/').catch(() => ({ data: [] })),
      ]);
      set({
        businessContext: bizRes.data,
        branches: branchRes.data || [],
      });
    } catch {
      // Handled by 401 interceptor if token expired
    }
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('business_user');
    set({ user: null, businessContext: null, branches: [], isAuthenticated: false });
  },
}));
