import { useEffect } from 'react'
import { useCustomerStore } from '@/store/customerStore'
import { useSessionStore }  from '@/store/sessionStore'
import Header               from '@/components/Header'
import AlertBar             from '@/components/alerts/AlertBar'
import ConversationPanel    from '@/components/conversation/ConversationPanel'
import CustomerProfile      from '@/components/sidebar/CustomerProfile'
import SentimentMonitor     from '@/components/sidebar/SentimentMonitor'
import DocumentOCR          from '@/components/sidebar/DocumentOCR'
import TokenQueue           from '@/components/TokenQueue'
import DualChannelIndicator from '@/components/DualChannelIndicator'

export default function Dashboard() {
  const loadCustomer = useCustomerStore(s => s.loadCustomer)
  const startSession = useSessionStore(s => s.startSession)

  useEffect(() => {
    // Auto-load demo customer + start session on mount
    loadCustomer('PUN-00294871')
    startSession(`sess-${Date.now()}`, 'Q-14')
  }, [loadCustomer, startSession])

  return (
    <div className="flex flex-col h-screen bg-bg overflow-hidden">
      <Header />
      <AlertBar />

      <div className="flex flex-1 overflow-hidden">
        {/* LEFT: Conversation */}
        <div className="flex flex-col flex-1 overflow-hidden border-r border-border">
          <DualChannelIndicator />
          <ConversationPanel />
          <TokenQueue />
        </div>

        {/* RIGHT: Sidebar */}
        <div className="w-[360px] flex flex-col overflow-hidden">
          <CustomerProfile />
          <SentimentMonitor />
          <DocumentOCR />
        </div>
      </div>
    </div>
  )
}