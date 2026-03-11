import { useParams, Link } from 'react-router-dom'
import { useState } from 'react'
import { motion } from 'framer-motion'
import Header from '@/components/Header'

// ── Demo Data (will be replaced by API call to /api/session/:id) ──
const DEMO_SESSION = {
    id: 'sess-001',
    customer: { name: 'Priya Sharma', cif: 'PUN-00294871', language: 'mr' },
    staff: { name: 'Amit Desai', id: 'staff-001' },
    branch: 'Pune Koregaon Park',
    token: 'Q-14',
    status: 'closed',
    duration: '8m 42s',
    created_at: '2026-03-10T09:30:00',
    closed_at: '2026-03-10T09:38:42',
    transcripts: [
        {
            speaker: 'customer', channel: 'A', language: 'mr',
            text: 'मला माझे कार्ड हरवले आहे. मला खूप काळजी वाटत आहे!',
            translation: 'I lost my card. I am very worried!',
            intent: 'lost_card', timestamp: '09:30:12',
        },
        {
            speaker: 'ai', channel: null, language: 'en',
            text: '🔴 CRITICAL: Lost card. Stress 78%. Initiate block → Card #4829.',
            timestamp: '09:30:13',
        },
        {
            speaker: 'staff', channel: 'B', language: 'en',
            text: "Don't worry, Priya ji. We'll block your card right now.",
            translation: 'काळजी करू नका, प्रिया जी. आम्ही आत्ताच तुमचे कार्ड ब्लॉक करतो.',
            timestamp: '09:30:22',
        },
        {
            speaker: 'customer', channel: 'A', language: 'mr',
            text: 'धन्यवाद. माझ्या खात्यातून कोणी पैसे काढले नाहीेत ना?',
            translation: "Thank you. Nobody withdrew money from my account, right?",
            intent: 'balance_enquiry', timestamp: '09:31:05',
        },
        {
            speaker: 'staff', channel: 'B', language: 'en',
            text: 'No unauthorized transactions found. Your balance is safe.',
            translation: 'कोणतेही अनधिकृत व्यवहार नाहीत. तुमची शिल्लक सुरक्षित आहे.',
            timestamp: '09:31:35',
        },
    ],
    actions: [
        { type: 'CARD_BLOCK', label: 'Card Blocked', time: '09:30:45', by: 'System' },
        { type: 'CARD_REISSUE', label: 'Re-issue Initiated', time: '09:32:10', by: 'Amit Desai' },
        { type: 'KYC_VERIFY', label: 'KYC Verified (Aadhaar)', time: '09:34:20', by: 'System' },
    ],
    documents: [
        { type: 'Aadhaar', status: 'verified', confidence: 0.97 },
    ],
    compliance: { score: 100, violations: [] },
    sentiment_avg: { stress: 0.58, emotion: 'distressed → calm' },
    summary: `### Session Summary\n\n**Customer**: Priya Sharma (CIF: PUN-00294871)\n**Intent**: Lost Credit Card — Urgency: Critical\n\n**Actions Taken**:\n1. ✅ Card #4829 blocked immediately\n2. ✅ Re-issue initiated (delivery: 3 business days)\n3. ✅ KYC reverified via Aadhaar\n4. ✅ Balance confirmed — no unauthorized transactions\n\n**Compliance**: All RBI disclosure norms followed.\n\n**Next Steps**: Customer to collect new card at branch with original ID proof.`,
}

export default function SessionPage() {
    const { id } = useParams()
    const [session] = useState(DEMO_SESSION)

    return (
        <div className="flex flex-col h-screen bg-bg overflow-hidden">
            <Header />

            <div className="flex-1 overflow-y-auto px-6 py-5">
                {/* Breadcrumb */}
                <div className="flex items-center gap-2 text-xs text-muted mb-5">
                    <Link to="/" className="hover:text-accent transition-colors">Dashboard</Link>
                    <span>›</span>
                    <Link to="/reports" className="hover:text-accent transition-colors">Reports</Link>
                    <span>›</span>
                    <span className="text-text font-mono">{id || session.id}</span>
                </div>

                {/* Header card */}
                <motion.div
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-surface2 border border-border rounded-xl p-5 mb-5"
                >
                    <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-3">
                            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-900 to-accent flex items-center justify-center font-syne font-extrabold text-lg">
                                {session.token}
                            </div>
                            <div>
                                <div className="font-syne font-bold text-lg">{session.customer.name}</div>
                                <div className="text-xs text-muted font-mono">CIF #{session.customer.cif} · Branch: {session.branch}</div>
                            </div>
                        </div>
                        <div className="flex items-center gap-3">
                            <span className={`px-3 py-1 rounded-lg text-xs font-bold uppercase border ${session.status === 'closed' ? 'bg-surface text-muted border-border' : 'bg-accent2/15 text-accent2 border-accent2/30'}`}>
                                {session.status}
                            </span>
                            <span className="text-sm text-muted font-mono">⏱ {session.duration}</span>
                        </div>
                    </div>

                    <div className="grid grid-cols-4 gap-3">
                        <MiniStat label="Staff" value={session.staff.name} />
                        <MiniStat label="Language" value={session.customer.language.toUpperCase()} />
                        <MiniStat label="Avg Stress" value={`${Math.round(session.sentiment_avg.stress * 100)}%`} />
                        <MiniStat label="Compliance" value={`${session.compliance.score}%`} />
                    </div>
                </motion.div>

                <div className="grid grid-cols-3 gap-5">
                    {/* LEFT: Transcript replay */}
                    <div className="col-span-2 bg-surface2 border border-border rounded-xl overflow-hidden">
                        <div className="px-4 py-3 border-b border-border text-[11px] font-syne font-bold text-muted uppercase tracking-widest">
                            📝 Conversation Transcript
                        </div>
                        <div className="p-4 space-y-3 max-h-[400px] overflow-y-auto">
                            {session.transcripts.map((t, i) => (
                                <motion.div
                                    key={i}
                                    initial={{ opacity: 0, x: t.speaker === 'staff' ? 12 : -12 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: i * 0.08 }}
                                    className={`flex gap-2 ${t.speaker === 'staff' ? 'flex-row-reverse text-right' : ''}`}
                                >
                                    <div className={`w-7 h-7 rounded-lg flex-shrink-0 flex items-center justify-center text-[10px] font-bold ${t.speaker === 'customer' ? 'bg-blue-900/60 text-accent' :
                                            t.speaker === 'staff' ? 'bg-green-900/60 text-accent2' :
                                                'bg-purple-900/60 text-purple-400'
                                        }`}>
                                        {t.speaker === 'customer' ? 'C' : t.speaker === 'staff' ? 'S' : 'AI'}
                                    </div>
                                    <div className={`max-w-md px-3 py-2 rounded-xl text-xs leading-relaxed ${t.speaker === 'customer' ? 'bg-surface border border-border rounded-tl-sm' :
                                            t.speaker === 'staff' ? 'bg-green-950/30 border border-green-900/40 rounded-tr-sm' :
                                                'bg-purple-950/30 border border-purple-900/30 rounded-tl-sm font-mono text-purple-200'
                                        }`}>
                                        <div className="text-[10px] text-muted mb-1 font-mono">{t.timestamp}</div>
                                        {t.text}
                                        {t.translation && (
                                            <div className="mt-1.5 pt-1.5 border-t border-border/50 text-[10px] text-muted italic">
                                                {t.translation}
                                            </div>
                                        )}
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    </div>

                    {/* RIGHT: Actions + Documents + Summary */}
                    <div className="space-y-4">
                        {/* Actions */}
                        <div className="bg-surface2 border border-border rounded-xl overflow-hidden">
                            <div className="px-4 py-3 border-b border-border text-[11px] font-syne font-bold text-muted uppercase tracking-widest">
                                ⚡ Actions Taken
                            </div>
                            <div className="p-3 space-y-2">
                                {session.actions.map((a, i) => (
                                    <div key={i} className="flex items-center gap-2 px-3 py-2 bg-surface rounded-lg border border-border">
                                        <span className="text-accent2 text-sm">✓</span>
                                        <div className="flex-1">
                                            <div className="text-xs font-semibold">{a.label}</div>
                                            <div className="text-[10px] text-muted font-mono">{a.time} · {a.by}</div>
                                        </div>
                                        <span className="text-[9px] text-muted font-mono uppercase bg-surface2 px-1.5 py-0.5 rounded border border-border">
                                            {a.type}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Documents */}
                        <div className="bg-surface2 border border-border rounded-xl overflow-hidden">
                            <div className="px-4 py-3 border-b border-border text-[11px] font-syne font-bold text-muted uppercase tracking-widest">
                                📄 Documents Verified
                            </div>
                            <div className="p-3 space-y-2">
                                {session.documents.map((d, i) => (
                                    <div key={i} className="flex items-center justify-between px-3 py-2 bg-surface rounded-lg border border-border text-xs">
                                        <span className="font-semibold">{d.type}</span>
                                        <span className="text-accent2 font-mono">✓ {d.status} ({Math.round(d.confidence * 100)}%)</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Compliance */}
                        <div className="bg-surface2 border border-border rounded-xl p-4">
                            <div className="text-[11px] font-syne font-bold text-muted uppercase tracking-widest mb-2">
                                ✅ RBI Compliance
                            </div>
                            <div className="text-2xl font-syne font-extrabold text-accent2">{session.compliance.score}%</div>
                            <div className="text-[10px] text-muted mt-1">
                                {session.compliance.violations.length === 0 ? 'No violations detected' : `${session.compliance.violations.length} violations`}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Session Summary */}
                <motion.div
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="bg-surface2 border border-border rounded-xl p-5 mt-5"
                >
                    <div className="text-[11px] font-syne font-bold text-muted uppercase tracking-widest mb-3">
                        📋 AI-Generated Session Summary
                    </div>
                    <div className="text-sm leading-relaxed whitespace-pre-line text-text/90 font-mono">
                        {session.summary}
                    </div>
                </motion.div>
            </div>
        </div>
    )
}

function MiniStat({ label, value }) {
    return (
        <div className="p-2.5 bg-surface rounded-lg border border-border text-center">
            <div className="text-[10px] text-muted uppercase tracking-wide mb-0.5">{label}</div>
            <div className="text-sm font-syne font-bold">{value}</div>
        </div>
    )
}
