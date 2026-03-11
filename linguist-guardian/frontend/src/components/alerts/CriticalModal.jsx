import { motion, AnimatePresence } from 'framer-motion'
import { useSessionStore } from '@/store/sessionStore'

/**
 * CriticalModal — full-screen overlay for critical banking alerts.
 * Appears when intent urgency is 'critical' (lost card, fraud, etc.).
 * Forces staff acknowledgment before dismissal.
 */
export default function CriticalModal({ alert, onDismiss }) {
  const addAction = useSessionStore(s => s.addAction)

  if (!alert) return null

  const handleAction = (action) => {
    addAction({
      type: action.code,
      detail: action.label,
      status: 'initiated',
      timestamp: new Date().toISOString(),
    })
    if (action.dismiss) onDismiss?.()
  }

  const SEVERITY_STYLES = {
    critical: {
      bg: 'from-critical/20 to-critical/5',
      border: 'border-critical/40',
      icon: '🚨',
      glow: 'shadow-[0_0_60px_rgba(255,51,85,0.3)]',
    },
    high: {
      bg: 'from-gold/20 to-gold/5',
      border: 'border-gold/40',
      icon: '⚠️',
      glow: 'shadow-[0_0_60px_rgba(255,170,0,0.2)]',
    },
  }

  const style = SEVERITY_STYLES[alert.severity] || SEVERITY_STYLES.critical

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm"
      >
        <motion.div
          initial={{ scale: 0.9, y: 20 }}
          animate={{ scale: 1, y: 0 }}
          exit={{ scale: 0.9, y: 20 }}
          className={`
            w-[520px] rounded-2xl p-6 bg-gradient-to-b ${style.bg}
            border ${style.border} ${style.glow}
          `}
        >
          {/* Header */}
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-xl bg-critical/20 flex items-center justify-center text-2xl animate-pulse">
              {style.icon}
            </div>
            <div>
              <div className="font-syne font-bold text-lg text-critical tracking-tight">
                {alert.title || 'CRITICAL ALERT'}
              </div>
              <div className="text-xs text-muted mt-0.5">
                Requires immediate staff action
              </div>
            </div>
          </div>

          {/* Message */}
          <div className="bg-surface/50 rounded-xl p-4 mb-4 border border-border">
            <p className="text-sm text-white/90 leading-relaxed">
              {alert.message}
            </p>
          </div>

          {/* Customer Info */}
          {alert.customer && (
            <div className="flex items-center gap-3 mb-4 px-4 py-2.5 bg-surface2/50 rounded-lg border border-border">
              <div className="w-8 h-8 rounded-lg bg-accent/20 flex items-center justify-center text-xs font-bold text-accent">
                {alert.customer.name?.split(' ').map(n => n[0]).join('')}
              </div>
              <div>
                <div className="text-xs font-medium">{alert.customer.name}</div>
                <div className="text-[10px] text-muted">CIF {alert.customer.id}</div>
              </div>
            </div>
          )}

          {/* AI Steps */}
          {alert.steps && alert.steps.length > 0 && (
            <div className="mb-4">
              <div className="text-[10px] text-muted uppercase tracking-wider mb-2 font-mono">
                AI Recommended Steps
              </div>
              <ol className="space-y-1.5">
                {alert.steps.map((step, i) => (
                  <li key={i} className="flex items-start gap-2 text-xs text-white/80">
                    <span className="w-5 h-5 rounded-full bg-accent/20 text-accent flex items-center justify-center text-[10px] flex-shrink-0 mt-0.5">
                      {i + 1}
                    </span>
                    {step}
                  </li>
                ))}
              </ol>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex items-center gap-2">
            {(alert.actions || []).map((action, i) => (
              <button
                key={i}
                onClick={() => handleAction(action)}
                className={`flex-1 px-4 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                  i === 0
                    ? 'bg-critical text-white hover:bg-critical/80 shadow-lg shadow-critical/20'
                    : 'bg-surface2 border border-border text-muted hover:border-accent hover:text-accent'
                }`}
              >
                {action.label}
              </button>
            ))}
            <button
              onClick={onDismiss}
              className="px-4 py-2.5 rounded-xl text-xs text-muted hover:text-white transition-colors"
            >
              Dismiss
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}
