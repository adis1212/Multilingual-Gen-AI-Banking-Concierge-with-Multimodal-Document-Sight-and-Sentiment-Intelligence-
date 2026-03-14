import { useOrchestratorStore } from '@/store/orchestratorStore'

const urgencyConfig = {
  high: {
    border: 'border-red-500',
    bg: 'bg-red-50',
    text: 'text-red-700',
    badge: 'bg-red-100 text-red-700',
    icon: '🔴',
    label: 'HIGH',
  },
  medium: {
    border: 'border-amber-500',
    bg: 'bg-amber-50',
    text: 'text-amber-700',
    badge: 'bg-amber-100 text-amber-700',
    icon: '🟠',
    label: 'MEDIUM',
  },
  low: {
    border: 'border-gray-300',
    bg: 'bg-gray-50',
    text: 'text-gray-700',
    badge: 'bg-gray-100 text-gray-700',
    icon: '🟢',
    label: 'LOW',
  },
}

export default function RoutingDecisionPanel() {
  const { decision, loading, error } = useOrchestratorStore()

  return (
    <div className="p-4 border-b border-border">
      <div className="text-[11px] font-syne font-bold text-muted uppercase tracking-widest mb-3 flex items-center gap-2">
        🤖 Routing Decision
      </div>

      {loading && (
        <div className="flex items-center gap-2 p-3 bg-surface2 rounded-xl border border-border animate-pulse">
          <div className="w-2 h-2 rounded-full bg-accent animate-ping" />
          <span className="text-xs text-muted">Routing conversation…</span>
        </div>
      )}

      {!loading && error && (
        <div className="flex items-center gap-2 p-2 rounded-lg border border-red-500/30 bg-red-50/10">
          <span className="text-[10px] text-red-400">⚠ Routing unavailable</span>
        </div>
      )}

      {!loading && !decision && !error && (
        <div className="p-3 bg-surface2 rounded-xl border border-border text-center">
          <span className="text-xs text-muted">Awaiting transcript…</span>
        </div>
      )}

      {!loading && decision && (() => {
        const urgency = decision.urgency in urgencyConfig ? decision.urgency : 'low'
        const cfg = urgencyConfig[urgency]
        return (
          <div className={`rounded-xl border-2 ${cfg.border} ${cfg.bg} p-3 space-y-2`}>
            {/* Urgency badge */}
            <div className="flex items-center justify-between">
              <span className={`text-[10px] font-syne font-bold uppercase tracking-widest ${cfg.text}`}>
                {cfg.icon} Urgency: {cfg.label}
              </span>
              <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${cfg.badge}`}>
                {urgency}
              </span>
            </div>

            {/* Agent */}
            <div>
              <div className="text-[10px] text-muted uppercase tracking-wider mb-0.5">Agent</div>
              <div className={`text-xs font-syne font-bold ${cfg.text}`}>
                {decision.agent.replace(/_/g, ' ')}
              </div>
            </div>

            {/* Recommended action */}
            <div>
              <div className="text-[10px] text-muted uppercase tracking-wider mb-0.5">Recommended Action</div>
              <div className="text-xs text-foreground leading-relaxed">
                {decision.recommended_action}
              </div>
            </div>
          </div>
        )
      })()}
    </div>
  )
}
