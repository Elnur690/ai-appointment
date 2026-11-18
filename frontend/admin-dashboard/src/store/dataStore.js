import { create } from 'zustand';
import apiClient from '../api/client';

export const useDataStore = create((set, get) => ({
  analytics: {
    total_businesses: 0,
    active_subscriptions: 0,
    trial_businesses: 0,
    suspended_businesses: 0,
    mrr_usd: 0,
    mrr_azn: 0,
    arr_azn: 0,
    total_settled_revenue_azn: 0,
    total_appointments: 0,
    completed_appointments: 0,
    cancelled_appointments: 0,
    pending_appointments: 0,
    total_customers: 0,
    total_messages: 0,
    inbound_messages: 0,
    outbound_ai_messages: 0,
    total_messages_this_month: 0,
    total_resellers: 0,
    total_ai_tokens_used: 0,
    total_ai_spend_usd: 0,
    total_ai_spend_azn: 0,
    net_platform_margin_azn: 0,
    ai_spend_per_business: [],
  },
  businesses: [],
  plans: [],
  subscriptions: [],
  resellers: [],
  paymentGateways: [
    {
      provider: 'cash',
      name: 'Cash Payment (At Venue)',
      description: 'In-person cash & POS terminal payments recorded at the salon, clinic, or studio.',
      enabled: true,
      requires_credentials: false,
    },
    {
      provider: 'payriff',
      name: 'Payriff Payment Gateway',
      description: 'Online card checkout and automated no-show deposit links via Payriff API.',
      enabled: true,
      requires_credentials: true,
    },
    {
      provider: 'paymegate',
      name: 'Paymegate Payment Gateway',
      description: 'Online card & crypto checkout via official Paymegate Merchant API v1 (api.paymegate.com).',
      enabled: true,
      requires_credentials: true,
    },
  ],
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

  fetchPaymentGateways: async () => {
    try {
      const res = await apiClient.get('/saas-admin/payment-gateways');
      if (Array.isArray(res.data) && res.data.length > 0) {
        set({ paymentGateways: res.data });
      }
    } catch (err) {
      set({ error: err.response?.data?.detail || err.message });
    }
  },

  togglePaymentGateway: async (provider, enabled) => {
    try {
      await apiClient.put(`/saas-admin/payment-gateways/${provider}`, { enabled });
      await get().fetchPaymentGateways();
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
        trialEndsAt: b.trial_ends_at || null,
        trialDaysRemaining: b.trial_days_remaining ?? 0,
        trialFeaturesOverride: b.trial_features_override || {},
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
        ...p,
        id: p.id,
        name: p.name,
        price_num: p.price,
        price: `${p.price} AZN/mo`,
        message_limit: p.message_limit,
        allows_free_trial: p.allows_free_trial !== false,
        trial_days: p.trial_days ?? 14,
        trial_features: p.trial_features || {},
        limits: p.message_limit >= 100000 ? 'Unlimited messages' : `${Number(p.message_limit).toLocaleString()} messages`,
        allows_whatsapp: p.allows_whatsapp !== false,
        allows_instagram: Boolean(p.allows_instagram || p.allows_omnichannel_messaging),
        allows_telegram: Boolean(p.allows_telegram || p.allows_omnichannel_messaging),
        allows_online_payments: Boolean(p.allows_online_payments),
        allows_voice_messages: Boolean(p.allows_voice_messages),
        allows_custom_domain: Boolean(p.allows_custom_domain),
        features: p.features || {},
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

  createBusiness: async (payload) => {
    const res = await apiClient.post('/saas-admin/businesses', payload);
    await get().fetchBusinesses();
    await get().fetchAnalytics();
    return res.data;
  },

  updateBusinessStatus: async (id, status, extra = {}) => {
    await apiClient.put(`/saas-admin/businesses/${id}/status`, { status, ...extra });
    await get().fetchBusinesses();
    await get().fetchAnalytics();
  },

  createPlan: async (plan) => {
    const parsedPrice = parseFloat(String(plan.price).replace(/[^0-9.]/g, '')) || 49.0;
    const parsedLimit = parseInt(String(plan.limits).replace(/[^0-9]/g, ''), 10) || 2000;
    await apiClient.post('/saas-admin/plans', {
      name: plan.name,
      price: parsedPrice,
      max_branches: Number(plan.max_branches || 1),
      max_whatsapp_numbers: Number(plan.max_whatsapp_numbers || 1),
      message_limit: parsedLimit,
      allows_free_trial: Boolean(plan.allows_free_trial),
      trial_days: Number(plan.trial_days ?? 14),
      trial_features: plan.trial_features || {},
      allows_whatsapp: plan.allows_whatsapp !== false,
      allows_instagram: Boolean(plan.allows_instagram),
      allows_telegram: Boolean(plan.allows_telegram),
      allows_omnichannel_messaging: Boolean(plan.allows_instagram || plan.allows_telegram || plan.allows_omnichannel_messaging),
      allows_voice_messages: Boolean(plan.allows_voice_messages),
      allows_dynamic_pricing: Boolean(plan.allows_dynamic_pricing),
      allows_winback_campaigns: Boolean(plan.allows_winback_campaigns),
      allows_discovery: Boolean(plan.allows_discovery),
      allows_online_payments: Boolean(plan.allows_online_payments),
      allows_gcal_sync: Boolean(plan.allows_gcal_sync),
      allows_apple_cal_sync: Boolean(plan.allows_apple_cal_sync),
      allows_custom_domain: Boolean(plan.allows_custom_domain),
      allows_no_show_deposits: Boolean(plan.allows_no_show_deposits),
      allows_emergency_reassignment: Boolean(plan.allows_emergency_reassignment),
      allows_growth_advisor: Boolean(plan.allows_growth_advisor),
      allows_loyalty_program: Boolean(plan.allows_loyalty_program),
      allows_combo_packages: Boolean(plan.allows_combo_packages),
      allows_group_bookings: Boolean(plan.allows_group_bookings),
      allows_product_upsells: Boolean(plan.allows_product_upsells),
      allows_branch_level_ai_tone: Boolean(plan.allows_branch_level_ai_tone),
      allows_geo_routing: Boolean(plan.allows_geo_routing),
      allows_shift_management: Boolean(plan.allows_shift_management),
      allows_cadence_engine: Boolean(plan.allows_cadence_engine),
      allows_gift_vouchers: Boolean(plan.allows_gift_vouchers),
      allows_flash_drops: Boolean(plan.allows_flash_drops),
      features: { assigned_model: plan.assigned_ai_model || 'gemini-3.5-flash' },
    });
    await get().fetchPlans();
  },

  updatePlan: async (id, updates) => {
    await apiClient.put(`/saas-admin/plans/${id}`, updates);
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
