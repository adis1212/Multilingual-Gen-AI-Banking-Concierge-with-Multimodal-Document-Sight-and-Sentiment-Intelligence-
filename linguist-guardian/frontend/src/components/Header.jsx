import { useState } from 'react'
import { useSessionStore }  from '@/store/sessionStore'
import { useCustomerStore } from '@/store/customerStore'
import { useSentimentStore } from '@/store/sentimentStore'
import toast from 'react-hot-toast'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function Header() {
  const { sessionId, tokenNumber, status, messages, actions, closeSession, resetSession } = useSessionStore()
  const { customer } = useCustomerStore()
  const resetSentiment = useSentimentStore(s => s.reset)
  const [summaryLoading, setSummaryLoading] = useState(false)

  const handleEndSession = () => {
    if (status === 'closed') {
      toast('Session already closed', { icon: '✅' })
      return
    }
    closeSession()
    resetSentiment()
    toast.success('Session ended successfully', { duration: 3000 })
  }

  const handleSummary = async () => {
    if (messages.length === 0) {
      toast('No conversation to summarize', { icon: 'ℹ️' })
      return
    }

    setSummaryLoading(true)
    try {
      // Try to generate summary through backend
      const { data } = await axios.post(`${API_URL}/api/session/close`, {
        session_id: sessionId,
      })
      toast.success(
        <div>
          <div className="font-bold mb-1">📋 Session Summary</div>
          <div className="text-xs opacity-80">{data.summary || 'Session closed. Summary generated.'}</div>
        </div>,
        { duration: 8000 }
      )
    } catch {
      // Fallback: generate local summary from messages
      const customerMsgs = messages.filter(m => m.speaker === 'customer').length
      const staffMsgs = messages.filter(m => m.speaker === 'staff').length
      const actionsCount = actions?.length || 0

      toast.success(
        <div>
          <div className="font-bold mb-1">📋 Session Summary</div>
          <div className="text-xs opacity-80">
            Messages: {messages.length} ({customerMsgs} customer, {staffMsgs} staff)<br/>
            Actions taken: {actionsCount}<br/>
            Token: {tokenNumber || 'N/A'}<br/>
            Customer: {customer?.name || 'Unknown'}
          </div>
        </div>,
        { duration: 6000 }
      )
    } finally {
      setSummaryLoading(false)
    }
  }

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
        <Badge dot={status === 'active' ? 'green' : 'red'}>
          Session {sessionId ? `#${sessionId.slice(-6).toUpperCase()}` : '—'} · Pune Koregaon
        </Badge>
        <Badge dot="blue">Staff: Amit Desai</Badge>
        <Badge dot="yellow">Token {tokenNumber || '—'} · 3 Waiting</Badge>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2">
        <button
          onClick={handleEndSession}
          disabled={status === 'closed'}
          className={`px-4 py-2 rounded-lg border text-sm transition-colors ${
            status === 'closed'
              ? 'border-border text-muted/50 cursor-not-allowed'
              : 'border-border text-muted hover:border-critical hover:text-critical'
          }`}
        >
          {status === 'closed' ? '✓ Ended' : 'End Session'}
        </button>
        <button
          onClick={handleSummary}
          disabled={summaryLoading}
          className="px-4 py-2 rounded-lg bg-accent text-white text-sm font-medium hover:bg-accent/80 transition-colors disabled:opacity-50"
        >
          {summaryLoading ? '⏳ Generating...' : '📋 Summary'}
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