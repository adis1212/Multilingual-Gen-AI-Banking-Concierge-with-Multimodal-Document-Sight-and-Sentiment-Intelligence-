const MOCK_QUEUE = [
  { token: 'Q-14', label: 'Active',      status: 'active' },
  { token: 'Q-15', label: 'Waiting ~12m', status: 'waiting' },
  { token: 'Q-16', label: 'Waiting ~24m', status: 'waiting' },
  { token: 'Q-17', label: 'Waiting ~35m', status: 'waiting' },
]

export default function TokenQueue() {
  return (
    <div className="flex items-center gap-3 px-5 py-2.5 border-t border-border bg-surface overflow-x-auto">
      <span className="text-[11px] text-muted font-mono flex-shrink-0 uppercase tracking-wide">
        Token Queue:
      </span>
      {MOCK_QUEUE.map(q => (
        <div
          key={q.token}
          className={`flex-shrink-0 px-3 py-1.5 rounded-lg text-xs font-mono border transition-all ${
            q.status === 'active'
              ? 'bg-critical/10 border-critical/30 text-critical shadow-[0_0_12px_rgba(255,51,85,0.2)]'
              : 'bg-surface2 border-border text-muted'
          }`}
        >
          {q.status === 'active' ? '⚠ ' : ''}{q.token} · {q.label}
        </div>
      ))}
    </div>
  )
}