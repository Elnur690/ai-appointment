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

export const useAuthStore = create((set) => ({
  user: getSavedUser(),
  businessContext: null,
  branches: [],
  language: 'az',
  isAuthenticated: Boolean(localStorage.getItem('access_token')),
  setLanguage: (language) => set({ language }),

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