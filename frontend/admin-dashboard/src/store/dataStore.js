import { create } from 'zustand';
import apiClient from '../api/client';

export const useDataStore = create((set, get) => ({
  analytics: {
    total_businesses: 0,
    active_subscriptions: 0,
    mrr_usd: 0,
    total_messages_this_month: 0,
  },
  businesses: [],
  plans: [],
  subscriptions: [],
  resellers: [],
  loading: false,
  error: null,

  fetchAnalytics: async () => {
    try {
      const res = await apiClient.get('/saas-admin/analytics');
      set({ analytics: res.data });
    } catch (err) {
      set({ error: err.response?.data?.detail || err.message });
    }
  },

  fetchBusinesses: async () => {
    set({ loading: true, error: null });
    try {
      const res = await apiClient.get('/saas-admin/businesses');
      const mapped = (res.data || []).map((b) => ({
        id: b.id,
        name: b.name,
        owner: b.owner || '—',
        plan: b.plan || 'Starter',
        customDomain: b.custom_domain || '',
        resellerCode: b.reseller_code || '',
        status: b.status || (b.is_active ? 'active' : 'suspended'),
        branches: b.branches ?? 0,
        created: b.created_at ? b.created_at.slice(0, 10) : '—',
      }));
      set({ businesses: mapped, loading: false });
    } catch (err) {
      set({ loading: false, error: err.response?.data?.detail || err.message });
    }
  },

  fetchPlans: async () => {
    set({ loading: true, error: null });
    try {
      const res = await apiClient.get('/saas-admin/plans');
      const mapped = (res.data || []).map((p) => ({
        id: p.id,
        name: p.name,
        price_num: p.price,
        price: `${p.price} AZN/mo`,
        message_limit: p.message_limit,
        limits: p.message_limit >= 100000 ? 'Unlimited messages' : `${Number(p.message_limit).toLocaleString()} messages`,
        features: Array.isArray(p.features?.list)
          ? p.features.list.join(', ')
          : Object.keys(p.features || {}).join(', ') || 'AI Booking, Multi-Channel WhatsApp & Instagram',
      }));
      set({ plans: mapped, loading: false });
    } catch (err) {
      set({ loading: false, error: err.response?.data?.detail || err.message });
    }
  },

  fetchSubscriptions: async () => {
    set({ loading: true, error: null });
    try {
      const res = await apiClient.get('/saas-admin/subscriptions');
      set({ subscriptions: res.data || [], loading: false });
    } catch (err) {
      set({ loading: false, error: err.response?.data?.detail || err.message });
    }
  },

  fetchResellers: async () => {
    set({ loading: true, error: null });
    try {
      const res = await apiClient.get('/resellers/');
      set({ resellers: res.data || [], loading: false });
    } catch (err) {
      set({ loading: false, error: err.response?.data?.detail || err.message });
    }
  },

  updateBusinessStatus: async (id, status, extra = {}) => {
    await apiClient.put(`/saas-admin/businesses/${id}/status`, { status, ...extra });
    await get().fetchBusinesses();
    await get().fetchAnalytics();
  },

  createPlan: async (plan) => {
    const parsedPrice = parseFloat(String(plan.price).replace(/[^0-9.]/g, '')) || 49.0;
    const parsedLimit = parseInt(String(plan.limits).replace(/[^0-9]/g, ''), 10) || 2000;
    const featureList = String(plan.features || '')
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean);
    await apiClient.post('/saas-admin/plans', {
      name: plan.name,
      price: parsedPrice,
      message_limit: parsedLimit,
      features: { list: featureList },
    });
    await get().fetchPlans();
  },

  createReseller: async (reseller) => {
    await apiClient.post('/resellers/', {
      name: reseller.name,
      company_name: reseller.company_name || null,
      email: reseller.email,
      phone: reseller.phone || null,
      referral_code: reseller.referral_code,
      commission_rate_percent: Number(reseller.commission_rate_percent || 20),
      white_label_domain: reseller.white_label_domain || null,
    });
    await get().fetchResellers();
  },

  recordResellerPayout: async (id, amount) => {
    await apiClient.post(`/resellers/${id}/payouts`, {
      amount_azn: Number(amount),
      payment_method: 'bank_transfer',
    });
    await get().fetchResellers();
  },
}));
