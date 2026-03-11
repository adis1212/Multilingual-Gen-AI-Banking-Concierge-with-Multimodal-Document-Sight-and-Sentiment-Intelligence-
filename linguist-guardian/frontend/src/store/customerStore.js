import { create } from 'zustand'

export const useCustomerStore = create((set) => ({
  customer: null,
  isLoading: false,

  setCustomer: (customer) => set({ customer }),

  // Mock load — replace with real API call
  loadCustomer: async (cifId) => {
    set({ isLoading: true })
    await new Promise(r => setTimeout(r, 500))
    set({
      isLoading: false,
      customer: {
        id:             cifId || 'PUN-00294871',
        name:           'Priya Sharma',
        language:       'mr',
        cibil_score:    762,
        kyc_status:     'partial',
        account_balance: 124500,
        phone:          '+91-98765-43210',
        last_visit:     '2026-02-23',
        loan_status:    'none',
      }
    })
  },

  clearCustomer: () => set({ customer: null }),
}))