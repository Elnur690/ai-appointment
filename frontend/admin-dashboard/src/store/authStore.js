import { create } from 'zustand';

export const useAuthStore = create((set) => ({
  user: { name: 'Admin', email: 'admin@ai-appointment.com' }, // Mock user for now
  token: localStorage.getItem('access_token') || 'mock-token',
  language: 'az',
  isAuthenticated: true, // Set to true by default for scaffolding preview
  setLanguage: (language) => set({ language }),

  
  login: async (email, password) => {
    // Mock login
    const token = 'mock-jwt-token-123';
    localStorage.setItem('access_token', token);
    set({ 
      user: { name: 'Admin', email }, 
      token, 
      isAuthenticated: true 
    });
  },
  
  logout: () => {
    localStorage.removeItem('access_token');
    set({ user: null, token: null, isAuthenticated: false });
  },
  
  refreshToken: async () => {
    // Mock refresh
    console.log('Token refreshed');
  }
}));
