import { create } from 'zustand';

// Mock Data
const mockBusinesses = [
  { id: 1, name: 'Glow Salon', owner: 'Sarah J.', plan: 'Pro', status: 'active', branches: 2, created: '2023-10-01' },
  { id: 2, name: 'Elite Fitness', owner: 'Mike T.', plan: 'Starter', status: 'trial', branches: 1, created: '2023-11-15' },
  { id: 3, name: 'Smile Dental', owner: 'Dr. Smith', plan: 'Enterprise', status: 'active', branches: 5, created: '2023-09-20' },
  { id: 4, name: 'Quick Cuts', owner: 'John D.', plan: 'Starter', status: 'suspended', branches: 1, created: '2023-08-10' },
  { id: 5, name: 'Zen Spa', owner: 'Emma W.', plan: 'Pro', status: 'active', branches: 3, created: '2023-12-05' },
];

const mockPlans = [
  { id: 1, name: 'Starter', price: '$29/mo', limits: '500 messages', features: 'Basic AI, 1 Branch' },
  { id: 2, name: 'Pro', price: '$79/mo', limits: '2000 messages', features: 'Advanced AI, Up to 3 Branches' },
  { id: 3, name: 'Enterprise', price: '$199/mo', limits: 'Unlimited', features: 'Custom AI, Unlimited Branches' },
];

const mockSubscriptions = [
  { id: 1, business: 'Glow Salon', plan: 'Pro', status: 'active', period: 'Monthly', messagesUsed: '1,240 / 2,000' },
  { id: 2, business: 'Elite Fitness', plan: 'Starter', status: 'trial', period: 'Monthly', messagesUsed: '120 / 500' },
  { id: 3, business: 'Smile Dental', plan: 'Enterprise', status: 'active', period: 'Yearly', messagesUsed: '8,450 / ∞' },
];

export const useDataStore = create((set) => ({
  businesses: mockBusinesses,
  plans: mockPlans,
  subscriptions: mockSubscriptions,
  
  fetchBusinesses: async () => {
    // API call would go here
    set({ businesses: mockBusinesses });
  },
  
  fetchPlans: async () => {
    set({ plans: mockPlans });
  },
  
  updateBusinessStatus: (id, status) => {
    set((state) => ({
      businesses: state.businesses.map(b => b.id === id ? { ...b, status } : b)
    }));
  },
  
  createPlan: (plan) => {
    set((state) => ({
      plans: [...state.plans, { ...plan, id: state.plans.length + 1 }]
    }));
  },
}));
