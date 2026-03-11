import { create } from 'zustand'

export const useSessionStore = create((set, get) => ({
  sessionId:    null,
  staffId:      'staff-001',
  branchId:     'pune-koregaon',
  tokenNumber:  null,
  status:       'idle',        // idle | active | closed
  messages:     [],            // all conversation messages
  actions:      [],            // actions taken this session
  isRecording:  false,
  activeChannel: 'A',          // A = customer, B = staff

  // Start a new session
  startSession: (sessionId, tokenNumber) => set({
    sessionId,
    tokenNumber,
    status: 'active',
    messages: [],
    actions: [],
  }),

  // Add a message to conversation
  addMessage: (message) => set((state) => ({
    messages: [...state.messages, {
      id:        crypto.randomUUID(),
      timestamp: new Date().toISOString(),
      ...message,
    }]
  })),

  // Log an action taken
  addAction: (action) => set((state) => ({
    actions: [...state.actions, {
      id:        crypto.randomUUID(),
      timestamp: new Date().toISOString(),
      ...action,
    }]
  })),

  setRecording:  (val) => set({ isRecording: val }),
  setChannel:    (ch)  => set({ activeChannel: ch }),
  closeSession:  ()    => set({ status: 'closed', isRecording: false }),
  resetSession:  ()    => set({ sessionId: null, status: 'idle', messages: [], actions: [] }),
}))