import { useSessionStore } from '@/store/sessionStore'

function WaveBar({ color = 'bg-accent', delay = '0s' }) {
  return (
    <span
      className={`inline-block w-0.5 rounded-sm ${color} animate-bounce`}
      style={{ animationDelay: delay, height: `${8 + Math.random() * 12}px` }}
    />
  )
}

export default function DualChannelIndicator() {
  const { isRecording, activeChannel } = useSessionStore()

  return (
    <div className="flex items-center gap-3 px-5 py-2.5 bg-surface2 border-b border-border">
      {/* Customer Channel A */}
      <div className="flex flex-1 items-center gap-3 px-3 py-2 bg-surface border border-border rounded-lg">
        <div className="flex items-end gap-0.5 h-6">
          {[...Array(7)].map((_, i) => (
            <WaveBar key={i} color="bg-critical" delay={`${i * 0.1}s`} />
          ))}
        </div>
        <div>
          <div className="text-xs font-semibold text-muted uppercase tracking-wide">Customer Mic</div>
          <div className="text-[10px] text-muted/60">Ch. A · Marathi · 44kHz</div>
        </div>
      </div>

      <span className="text-[10px] text-muted font-mono">DUAL EAR</span>

      {/* Staff Channel B */}
      <div className="flex flex-1 items-center gap-3 px-3 py-2 bg-surface border border-border rounded-lg">
        <div className="flex items-end gap-0.5 h-6">
          {[...Array(7)].map((_, i) => (
            <WaveBar key={i} color="bg-accent" delay={`${i * 0.1}s`} />
          ))}
        </div>
        <div>
          <div className="text-xs font-semibold text-muted uppercase tracking-wide">Staff Mic</div>
          <div className="text-[10px] text-muted/60">Ch. B · English · 44kHz</div>
        </div>
      </div>
    </div>
  )
}