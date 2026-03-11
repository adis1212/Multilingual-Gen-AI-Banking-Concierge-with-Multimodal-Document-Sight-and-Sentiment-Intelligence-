import { useSentimentStore } from '@/store/sentimentStore'
import { LineChart, Line, ResponsiveContainer, Tooltip } from 'recharts'

export default function SentimentMonitor() {
  const { stressLevel, pitchRisePct, speechRate, volume, emotion, deescalate, tips, history } = useSentimentStore()

  // Mock data for demo
  const chartData = history.length > 2 ? history : [
    { stress_level: 0.3 }, { stress_level: 0.45 }, { stress_level: 0.6 },
    { stress_level: 0.55 }, { stress_level: 0.72 }, { stress_level: 0.78 },
  ]

  const stressPct  = Math.round((stressLevel || 0.78) * 100)
  const pitchPct   = pitchRisePct || 22
  const rate       = speechRate || 'fast'
  const vol        = volume || 'medium'
  const emo        = emotion || 'distressed'
  const shouldDeesc = deescalate !== undefined ? deescalate : true

  return (
    <div className="p-4 border-b border-border">
      <div className="text-[11px] font-syne font-bold text-muted uppercase tracking-widest mb-3 flex items-center gap-2">
        🧠 Real-time Sentiment
      </div>

      {/* Stress trend chart */}
      <div className="h-16 mb-3">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <Line type="monotone" dataKey="stress_level" stroke="#ff3355" strokeWidth={2} dot={false} />
            <Tooltip
              contentStyle={{ background: '#0e1118', border: '1px solid #1e2333', fontSize: 11 }}
              formatter={v => [`${Math.round(v * 100)}%`, 'Stress']}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Metrics grid */}
      <div className="grid grid-cols-2 gap-2 mb-3">
        <EmotionChip value={`${stressPct}%`}   label="Stress Level" color="text-critical" />
        <EmotionChip value={`+${pitchPct}%`}   label="Pitch Rise"   color="text-gold" />
        <EmotionChip value={rate.charAt(0).toUpperCase() + rate.slice(1)} label="Speech Rate" color="text-gold" />
        <EmotionChip value={vol.charAt(0).toUpperCase() + vol.slice(1)}   label="Volume"      color="text-accent2" />
      </div>

      {/* De-escalation card */}
      {shouldDeesc && (
        <div className="p-3 bg-gradient-to-br from-orange-950/60 to-surface border border-warn/20 rounded-xl">
          <div className="text-xs font-syne font-bold text-warn mb-2 flex items-center gap-1.5">
            🟠 De-escalation Tips
          </div>
          <ul className="space-y-1">
            {(tips.length > 0 ? tips : [
              'Offer complimentary refreshment',
              'Prioritize this token immediately',
              'Use a slower, empathetic tone',
              "Address them as 'ji' (respectful)",
            ]).map((tip, i) => (
              <li key={i} className="text-xs text-orange-300 pl-3 relative before:content-['›'] before:absolute before:left-0 before:text-warn before:font-bold">
                {tip}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

function EmotionChip({ value, label, color }) {
  return (
    <div className="p-2 bg-surface2 rounded-lg border border-border text-center">
      <div className={`font-syne font-bold text-lg ${color}`}>{value}</div>
      <div className="text-[10px] text-muted mt-0.5">{label}</div>
    </div>
  )
}