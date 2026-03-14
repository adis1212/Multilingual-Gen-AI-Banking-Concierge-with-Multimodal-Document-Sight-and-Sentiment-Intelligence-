import { create } from 'zustand'

export const useOrchestratorStore = create((set) => ({
  decision: null,   // latest RoutingDecision | null
  loading:  false,
  error:    null,

  setDecision: (d) => set({ decision: d }),
  setLoading:  (b) => set({ loading: b }),
  setError:    (e) => set({ error: e }),
  reset:       ()  => set({ decision: null, loading: false, error: null }),
}))
