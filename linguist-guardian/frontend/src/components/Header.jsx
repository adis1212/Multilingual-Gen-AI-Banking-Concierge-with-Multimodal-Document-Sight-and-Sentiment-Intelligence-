import { useSessionStore }  from '@/store/sessionStore'
import { useCustomerStore } from '@/store/customerStore'

export default function Header() {
  const { sessionId, tokenNumber, status } = useSessionStore()
  const { customer } = useCustomerStore()

  return (
    <header className="flex items-center justify-between px-6 py-3 border-b border-border bg-surface/80 backdrop-blur-lg sticky top-0 z-50">
      {/* Logo */}
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-accent to-accent2 flex items-center justify-center text-lg">
          🛡
        </div>
        <span className="font-syne font-extrabold text-lg tracking-tight">
          Linguist<span className="text-accent2">-Guardian</span>
        </span>
      </div>

      {/* Status badges */}
      <div className="flex items-center gap-3">
        <Badge dot="green">
          Session {sessionId ? `#${sessionId.slice(-6).toUpperCase()}` : '—'} · Pune Koregaon
        </Badge>
        <Badge dot="blue">Staff: Amit Desai</Badge>
        <Badge dot="yellow">Token {tokenNumber || '—'} · 3 Waiting</Badge>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2">
        <button className="px-4 py-2 rounded-lg border border-border text-muted text-sm hover:border-accent hover:text-accent transition-colors">
          End Session
        </button>
        <button className="px-4 py-2 rounded-lg bg-accent text-white text-sm font-medium hover:bg-accent/80 transition-colors">
          📋 Summary
        </button>
      </div>
    </header>
  )
}

function Badge({ dot, children }) {
  const dotColors = {
    green:  'bg-accent2',
    blue:   'bg-accent',
    yellow: 'bg-gold',
    red:    'bg-critical',
  }
  return (
    <div className="flex items-center gap-2 px-3 py-1.5 bg-surface2 border border-border rounded-full text-xs font-mono text-muted">
      <span className={`w-1.5 h-1.5 rounded-full ${dotColors[dot] || 'bg-muted'} animate-pulse`} />
      {children}
    </div>
  )
}