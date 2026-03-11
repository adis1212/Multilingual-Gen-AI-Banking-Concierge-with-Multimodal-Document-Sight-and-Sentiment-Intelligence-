import { motion } from 'framer-motion'

/**
 * AIAdvisory — displays the GPT-4o AI intent engine's analysis
 * as a dark card within the conversation panel.
 * Shows: intent, urgency badge, numbered staff steps, and banking processes.
 */
export default function AIAdvisory({ intent }) {
  if (!intent) return null

  const urgencyColors = {
    critical: 'bg-critical text-white',
    high:     'bg-gold text-black',
    medium:   'bg-accent text-white',
    low:      'bg-accent2 text-black',
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex gap-3 items-start my-3"
    >
      {/* AI avatar */}
      <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-accent to-accent2 flex items-center justify-center text-sm flex-shrink-0">
        AI
      </div>

      <div className="flex-1 max-w-[75%]">
        {/* Label */}
        <div className="flex items-center gap-2 mb-1.5">
          <span className="px-2 py-0.5 bg-accent/20 text-accent text-[10px] font-bold rounded-md tracking-wider">
            GPT-4O · INTENT ENGINE
          </span>
          <span className="text-[10px] text-muted">
            {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>

        {/* Card */}
        <div className="bg-surface2/80 border border-border rounded-xl p-4 space-y-3">
          {/* Main advisory */}
          <div className="flex items-start gap-2">
            <span className={`
              px-2 py-0.5 text-[10px] font-bold rounded-md uppercase tracking-wider flex-shrink-0
              ${urgencyColors[intent.urgency] || urgencyColors.medium}
            `}>
              {intent.urgency}
            </span>
            <p className="text-sm text-white/90 leading-relaxed">
              {intent.staff_advisory}
            </p>
          </div>

          {/* Staff steps */}
          {intent.suggested_actions && intent.suggested_actions.length > 0 && (
            <ol className="space-y-1.5 pl-1">
              {intent.suggested_actions.map((action, i) => (
                <li key={i} className="flex items-start gap-2 text-xs text-white/70">
                  <span className="w-5 h-5 rounded-full bg-accent/15 text-accent text-[10px] flex items-center justify-center flex-shrink-0 mt-0.5">
                    {i + 1}
                  </span>
                  {action.replace(/_/g, ' ').replace(/^./, c => c.toUpperCase())}
                </li>
              ))}
            </ol>
          )}

          {/* Banking processes */}
          {intent.banking_processes && intent.banking_processes.length > 0 && (
            <div className="flex flex-wrap gap-1.5 pt-1">
              {intent.banking_processes.map((proc, i) => (
                <span
                  key={i}
                  className="px-2 py-0.5 bg-surface border border-border text-[9px] font-mono text-muted rounded-md"
                >
                  {proc}
                </span>
              ))}
            </div>
          )}

          {/* Customer-language response */}
          {intent.response_in_customer_language && (
            <div className="pt-2 border-t border-border">
              <div className="text-[9px] text-muted uppercase tracking-wider mb-1 font-mono">
                Suggested response
              </div>
              <p className="text-xs text-gold/90 italic">
                "{intent.response_in_customer_language}"
              </p>
            </div>
          )}

          {/* Escalation flag */}
          {intent.escalate_to_manager && (
            <div className="flex items-center gap-2 pt-2 border-t border-critical/20">
              <span className="w-2 h-2 rounded-full bg-critical animate-pulse" />
              <span className="text-[10px] text-critical font-semibold">
                ⚡ ESCALATE TO MANAGER — situation requires supervisor attention
              </span>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  )
}
