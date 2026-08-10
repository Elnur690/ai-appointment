import { create } from 'zustand';

export const useAuthStore = create((set) => ({
  user: { name: 'Admin User', role: 'owner' },
  businessContext: { name: 'Glow Spa', id: 'b1' },
  language: 'az',
  isAuthenticated: true,
  setLanguage: (language) => set({ language }),
  login: (user) => set({ user, isAuthenticated: true }),
  logout: () => set({ user: null, isAuthenticated: false }),
}));