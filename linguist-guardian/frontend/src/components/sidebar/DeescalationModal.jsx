import { motion, AnimatePresence } from 'framer-motion'
import { useSentimentStore } from '@/store/sentimentStore'

/**
 * DeescalationModal — appears when stress level exceeds threshold.
 * Provides empathetic de-escalation tips and quick actions for staff.
 */
export default function DeescalationModal({ onDismiss }) {
  const { stressLevel, emotion, tips } = useSentimentStore()

  const shouldShow = stressLevel > 0.6 || emotion === 'distressed'

  if (!shouldShow) return null

  const DE_ESCALATION_TIPS = tips.length > 0 ? tips : [
    'Use a calm, measured tone when speaking',
    'Address the customer respectfully with "ji" suffix',
    'Acknowledge their frustration before offering solutions',
    'Offer complimentary water or tea',
    'Prioritize their token — skip to immediate service',
    'If frustrated about wait time, apologize sincerely',
    'Avoid technical banking jargon, use simple language',
  ]

  const QUICK_ACTIONS = [
    { icon: '☕', label: 'Offer Refreshment', code: 'OFFER_REFRESHMENT' },
    { icon: '⏩', label: 'Priority Token',    code: 'PRIORITY_TOKEN' },
    { icon: '👤', label: 'Call Manager',       code: 'CALL_MANAGER' },
    { icon: '📝', label: 'Log Complaint',      code: 'LOG_COMPLAINT' },
  ]

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: 20 }}
        className="bg-gradient-to-b from-gold/10 to-gold/5 border border-gold/30 rounded-xl p-4 shadow-lg shadow-gold/10"
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gold/20 flex items-center justify-center animate-pulse">
              🧘
            </div>
            <div>
              <div className="text-xs font-syne font-bold text-gold tracking-tight">
                DE-ESCALATION ADVISOR
              </div>
              <div className="text-[10px] text-gold/60">
                Stress: {Math.round(stressLevel * 100)}% · {emotion}
              </div>
            </div>
          </div>
          <button
            onClick={onDismiss}
            className="text-muted hover:text-white text-xs transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Stress Bar */}
        <div className="mb-3">
          <div className="w-full h-1.5 bg-surface2 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${Math.min(stressLevel * 100, 100)}%` }}
              className={`h-full rounded-full ${
                stressLevel > 0.7 ? 'bg-critical' : 'bg-gold'
              }`}
            />
          </div>
        </div>

        {/* Tips */}
        <div className="space-y-1.5 mb-3">
          {DE_ESCALATION_TIPS.slice(0, 4).map((tip, i) => (
            <div key={i} className="flex items-start gap-2 text-[11px] text-white/80">
              <span className="text-gold/80 flex-shrink-0">•</span>
              {tip}
            </div>
          ))}
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-2 gap-1.5">
          {QUICK_ACTIONS.map((action, i) => (
            <button
              key={i}
              className="flex items-center gap-1.5 px-2.5 py-2 bg-surface2/80 border border-border rounded-lg text-[10px] text-muted hover:border-gold/40 hover:text-gold transition-all"
            >
              <span>{action.icon}</span>
              {action.label}
            </button>
          ))}
        </div>
      </motion.div>
    </AnimatePresence>
  )
}
