import { useState } from 'react'
import { useSessionStore } from '@/store/sessionStore'
import { motion, AnimatePresence } from 'framer-motion'

export default function AlertBar() {
  const [visible, setVisible] = useState(true)
  const addAction = useSessionStore(s => s.addAction)

  if (!visible) return null

  const handleBlock = () => {
    addAction({ type: 'CARD_BLOCK', detail: 'Card #4829 blocked', status: 'done' })
    setVisible(false)
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0,   opacity: 1 }}
        exit={{    y: -40, opacity: 0 }}
        className="flex items-center gap-4 px-6 py-3 bg-critical/5 border-b border-critical/20"
      >
        <div className="w-8 h-8 rounded-lg bg-critical flex items-center justify-center text-sm flex-shrink-0 animate-pulse">
          ⚠️
        </div>

        <div className="flex-1">
          <div className="text-xs font-syne font-bold text-critical tracking-wide">
            🔴 CRITICAL — LOST CARD REPORTED · Immediate Action Required
          </div>
          <div className="text-[11px] text-critical/60 mt-0.5">
            Customer Priya Sharma reported card ending 4829 as lost. Auto-block initiated. Re-issue flow ready.
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleBlock}
            className="px-3 py-1.5 bg-critical text-white text-xs font-medium rounded-lg hover:bg-critical/80 transition-colors"
          >
            Block Card Now
          </button>
          <button className="px-3 py-1.5 bg-surface2 border border-border text-xs rounded-lg hover:border-accent transition-colors">
            Start Re-Issue
          </button>
          <button
            onClick={() => setVisible(false)}
            className="px-3 py-1.5 bg-surface2 border border-border text-xs rounded-lg hover:border-muted transition-colors"
          >
            Dismiss
          </button>
        </div>
      </motion.div>
    </AnimatePresence>
  )
}