import { create } from 'zustand';

export const useAppointmentStore = create((set) => ({
  appointments: [
    { id: 1, title: 'Haircut', status: 'confirmed', start: new Date(), staffId: 1, customer: 'John Doe' }
  ],
  filters: {},
  setFilters: (filters) => set({ filters }),
}));\n