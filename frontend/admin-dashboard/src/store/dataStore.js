import { create } from 'zustand';

// Initial Seed / Fallback Data for Randevu.vip
const mockBusinesses = [
  { id: 1, name: 'Glow Salon Baku', owner: 'Sarah J.', plan: 'Pro', customDomain: 'booking.glowsalon.az', resellerCode: 'PARTNER-BAKU', status: 'active', branches: 2, created: '2026-08-01' },
  { id: 2, name: 'Elite Barber Club', owner: 'Murad T.', plan: 'Starter', customDomain: '', resellerCode: 'PARTNER-BAKU', status: 'trial', branches: 1, created: '2026-08-15' },
  { id: 3, name: 'Smile Dental Clinic', owner: 'Dr. Rauf', plan: 'Enterprise', customDomain: 'smiledental.az', resellerCode: 'DIGITAL-AZ', status: 'active', branches: 5, created: '2026-07-20' },
  { id: 4, name: 'Quick Cuts Studio', owner: 'Elvin D.', plan: 'Starter', customDomain: '', resellerCode: '', status: 'suspended', branches: 1, created: '2026-06-10' },
  { id: 5, name: 'Zen Aesthetic Spa', owner: 'Leyla W.', plan: 'Pro', customDomain: 'zenspa.randevu.vip', resellerCode: 'PARTNER-BAKU', status: 'active', branches: 3, created: '2026-09-05' },
];

const mockPlans = [
  { id: 1, name: 'Starter', price: '$29/mo', limits: '1,000 messages', features: 'Gemini 3.5 Flash, 1 Branch' },
  { id: 2, name: 'Pro', price: '$79/mo', limits: '5,000 messages', features: 'Claude 3.7 Sonnet, Cadence Engine, Gift Vouchers, Flash Drops' },
  { id: 3, name: 'Enterprise', price: '$199/mo', limits: 'Unlimited', features: 'GPT-4o, Custom Domain (cname.randevu.vip), All 20 Features' },
];

const mockSubscriptions = [
  { id: 1, business: 'Glow Salon Baku', plan: 'Pro', status: 'active', period: 'Monthly', messagesUsed: '1,240 / 5,000' },
  { id: 2, business: 'Elite Barber Club', plan: 'Starter', status: 'trial', period: 'Monthly', messagesUsed: '120 / 1,000' },
  { id: 3, business: 'Smile Dental Clinic', plan: 'Enterprise', status: 'active', period: 'Yearly', messagesUsed: '8,450 / ∞' },
];

const mockResellers = [
  {
    id: 'res-1',
    name: 'Kamran Əliyev',
    company_name: 'Baku Digital Agency MMC',
    email: 'kamran@bakudigital.az',
    phone: '+994 50 211 33 44',
    referral_code: 'PARTNER-BAKU',
    referral_url: 'https://randevu.vip/register?ref=PARTNER-BAKU',
    commission_rate_percent: 25,
    white_label_domain: 'partner.bakudigital.az',
    referred_businesses_count: 8,
    active_businesses_count: 7,
    total_mrr_generated_azn: 840.0,
    monthly_commission_azn: 210.0,
    total_earned_azn: 1260.0,
    total_paid_azn: 1050.0,
    pending_payout_azn: 210.0,
    status: 'active',
  },
  {
    id: 'res-2',
    name: 'Aysel Həsənova',
    company_name: 'BeautyTech Consulting',
    email: 'aysel@beautytech.az',
    phone: '+994 55 440 12 90',
    referral_code: 'DIGITAL-AZ',
    referral_url: 'https://randevu.vip/register?ref=DIGITAL-AZ',
    commission_rate_percent: 20,
    white_label_domain: 'booking.beautytech.az',
    referred_businesses_count: 4,
    active_businesses_count: 4,
    total_mrr_generated_azn: 516.0,
    monthly_commission_azn: 103.2,
    total_earned_azn: 516.0,
    total_paid_azn: 412.8,
    pending_payout_azn: 103.2,
    status: 'active',
  },
];

export const useDataStore = create((set) => ({
  businesses: mockBusinesses,
  plans: mockPlans,
  subscriptions: mockSubscriptions,
  resellers: mockResellers,

  fetchBusinesses: async () => {
    set({ businesses: mockBusinesses });
  },

  fetchPlans: async () => {
    set({ plans: mockPlans });
  },

  updateBusinessStatus: (id, status) => {
    set((state) => ({
      businesses: state.businesses.map((b) => (b.id === id ? { ...b, status } : b)),
    }));
  },

  createPlan: (plan) => {
    set((state) => ({
      plans: [...state.plans, { ...plan, id: state.plans.length + 1 }],
    }));
  },

  createReseller: (reseller) => {
    const code = (reseller.referral_code || 'PARTNER-NEW').toUpperCase().replace(/\s+/g, '-');
    const newEntry = {
      id: `res-${Date.now()}`,
      name: reseller.name,
      company_name: reseller.company_name || 'Independent Partner',
      email: reseller.email,
      phone: reseller.phone || '+994 50 000 00 00',
      referral_code: code,
      referral_url: `https://randevu.vip/register?ref=${code}`,
      commission_rate_percent: Number(reseller.commission_rate_percent || 20),
      white_label_domain: reseller.white_label_domain || '',
      referred_businesses_count: 0,
      active_businesses_count: 0,
      total_mrr_generated_azn: 0,
      monthly_commission_azn: 0,
      total_earned_azn: 0,
      total_paid_azn: 0,
      pending_payout_azn: 0,
      status: 'active',
    };
    set((state) => ({
      resellers: [newEntry, ...state.resellers],
    }));
  },

  recordResellerPayout: (id, amount) => {
    set((state) => ({
      resellers: state.resellers.map((r) => {
        if (r.id !== id) return r;
        const paid = Number(r.total_paid_azn) + Number(amount);
        const pending = Math.max(0, Number(r.pending_payout_azn) - Number(amount));
        return { ...r, total_paid_azn: paid, pending_payout_azn: pending };
      }),
    }));
  },
}));
