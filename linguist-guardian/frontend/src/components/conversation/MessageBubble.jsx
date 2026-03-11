import { motion } from 'framer-motion'

const URGENCY_COLORS = {
  critical: 'text-critical border-critical/30 bg-critical/10',
  high:     'text-warn border-warn/30 bg-warn/10',
  medium:   'text-gold border-gold/30 bg-gold/10',
  low:      'text-accent border-accent/30 bg-accent/10',
}

export default function MessageBubble({ message }) {
  const { speaker, text, translation, language, intent, timestamp } = message
  const time = new Date(timestamp).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })

  if (speaker === 'ai') return <AIBubble text={text} time={time} />
  if (speaker === 'staff') return <StaffBubble message={message} time={time} />
  return <CustomerBubble message={message} time={time} intent={intent} />
}

function CustomerBubble({ message, time, intent }) {
  const { text, translation, language } = message
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex gap-3"
    >
      <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-900 to-accent flex items-center justify-center font-syne font-bold text-sm flex-shrink-0">
        P
      </div>
      <div className="max-w-lg">
        <div className="flex items-center gap-2 mb-1.5">
          <span className="text-xs text-muted">Priya Sharma</span>
          <span className="px-1.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wide bg-accent/10 text-accent border border-accent/20">
            {language?.toUpperCase()}
          </span>
          <span className="text-[10px] text-muted/50 ml-auto">{time}</span>
        </div>
        <div className="px-4 py-3 bg-surface2 border border-border rounded-2xl rounded-tl-sm text-sm leading-relaxed">
          {text}
          {translation && (
            <div className="mt-2 pt-2 border-t border-border/50 text-xs text-muted italic border-l-2 border-l-accent pl-2">
              <span className="text-text/80 not-italic font-medium">Translation: </span>{translation}
            </div>
          )}
          {intent && (
            <div className={`mt-2 inline-flex items-center gap-1.5 px-2 py-1 rounded text-[11px] font-mono font-semibold border ${URGENCY_COLORS[intent.urgency] || URGENCY_COLORS.low}`}>
              {intent.urgency === 'critical' ? '⚠' : '💡'} INTENT: {intent.intent?.replace('_', ' ').toUpperCase()}
            </div>
          )}
        </div>
      </div>
    </motion.div>
  )
}

function StaffBubble({ message, time }) {
  const { text, translation } = message
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex gap-3 flex-row-reverse"
    >
      <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-green-900 to-accent2 flex items-center justify-center font-syne font-bold text-sm flex-shrink-0">
        A
      </div>
      <div className="max-w-lg">
        <div className="flex items-center gap-2 mb-1.5 flex-row-reverse">
          <span className="text-xs text-muted">Amit Desai (Staff)</span>
          <span className="px-1.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wide bg-accent2/10 text-accent2 border border-accent2/20">EN</span>
          <span className="text-[10px] text-muted/50 mr-auto">{time}</span>
        </div>
        <div className="px-4 py-3 bg-green-950/30 border border-green-900/40 rounded-2xl rounded-tr-sm text-sm leading-relaxed text-right">
          {text}
          {translation && (
            <div className="mt-2 pt-2 border-t border-green-900/30 text-xs text-muted italic border-r-2 border-r-accent2 pr-2 text-right">
              <span className="text-text/80 not-italic font-medium">→ Marathi (ElevenLabs): </span>{translation}
            </div>
          )}
        </div>
      </div>
    </motion.div>
  )
}

function AIBubble({ text, time }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex gap-3"
    >
      <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-purple-900 to-purple-600 flex items-center justify-center font-syne font-extrabold text-xs flex-shrink-0">
        AI
      </div>
      <div className="max-w-lg">
        <div className="flex items-center gap-2 mb-1.5">
          <span className="px-1.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wide bg-purple-900/30 text-purple-400 border border-purple-800/30">
            GPT-4o · Intent Engine
          </span>
          <span className="text-[10px] text-muted/50 ml-auto">{time}</span>
        </div>
        <div className="px-4 py-3 bg-gradient-to-br from-purple-950/40 to-surface border border-purple-900/30 rounded-2xl rounded-tl-sm text-sm font-mono leading-relaxed whitespace-pre-line text-purple-100/90">
          {text}
        </div>
      </div>
    </motion.div>
  )
}