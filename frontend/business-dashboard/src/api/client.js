import axios from 'axios';

const resolveBaseUrl = () => {
  if (import.meta.env.VITE_API_URL) {
    return `${import.meta.env.VITE_API_URL.replace(/\/$/, '')}/api/v1`;
  }
  if (typeof window !== 'undefined' && window.location.hostname.endsWith('randevu.vip')) {
    return 'https://api.randevu.vip/api/v1';
  }
  return 'http://localhost:22800/api/v1';
};

const api = axios.create({
  baseURL: resolveBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token') || localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default api;
