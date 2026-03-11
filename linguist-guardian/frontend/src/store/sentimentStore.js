import { create } from 'zustand'

export const useSentimentStore = create((set) => ({
  stressLevel:    0,
  pitchRisePct:   0,
  speechRate:     'normal',
  volume:         'medium',
  emotion:        'neutral',
  deescalate:     false,
  tips:           [],
  history:        [],          // last 20 readings for chart

  updateSentiment: (data) => set((state) => {
    const entry = { ...data, time: Date.now() }
    const history = [...state.history.slice(-19), entry]
    return {
      stressLevel:  data.stress_level  ?? state.stressLevel,
      pitchRisePct: data.pitch_rise_pct ?? state.pitchRisePct,
      speechRate:   data.speech_rate   ?? state.speechRate,
      volume:       data.volume        ?? state.volume,
      emotion:      data.emotion       ?? state.emotion,
      deescalate:   data.deescalate    ?? state.deescalate,
      tips:         data.tips          ?? state.tips,
      history,
    }
  }),

  reset: () => set({
    stressLevel: 0, pitchRisePct: 0, speechRate: 'normal',
    volume: 'medium', emotion: 'neutral', deescalate: false,
    tips: [], history: [],
  }),
}))