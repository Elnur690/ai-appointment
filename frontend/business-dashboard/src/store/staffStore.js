import { create } from 'zustand';

export const useStaffStore = create((set) => ({
  staffList: [
    { id: 1, name: 'Alice Smith', role: 'Stylist' },
    { id: 2, name: 'Bob Jones', role: 'Massage Therapist' }
  ],
}));\n