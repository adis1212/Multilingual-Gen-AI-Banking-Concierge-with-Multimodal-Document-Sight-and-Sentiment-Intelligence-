import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { LineChart, Line, BarChart, Bar, ResponsiveContainer, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts'
import Header from '@/components/Header'
import dayjs from 'dayjs'

// ── Demo Data ──────────────────────────────────────────
const DEMO_SESSIONS = [
    {
        id: 'sess-001', customer: 'Priya Sharma', cif: 'PUN-00294871', staff: 'Amit Desai',
        branch: 'Pune Koregaon Park', token: 'Q-14', intent: 'lost_card', urgency: 'critical',
        emotion: 'distressed', status: 'closed', duration: '8m 42s',
        created_at: '2026-03-10T09:30:00', summary: 'Card block initiated, re-issue processed.',
    },
    {
        id: 'sess-002', customer: 'Rajesh Patil', cif: 'PUN-00318724', staff: 'Sneha Joshi',
        branch: 'Pune Koregaon Park', token: 'Q-15', intent: 'loan_query', urgency: 'medium',
        emotion: 'calm', status: 'closed', duration: '12m 05s',
        created_at: '2026-03-10T10:15:00', summary: 'Home loan eligibility checked, 1.2Cr pre-approved.',
    },
    {
        id: 'sess-003', customer: 'Anita Kulkarni', cif: 'PUN-00287945', staff: 'Amit Desai',
        branch: 'Pune Koregaon Park', token: 'Q-16', intent: 'kyc_update', urgency: 'low',
        emotion: 'calm', status: 'closed', duration: '5m 18s',
        created_at: '2026-03-10T11:00:00', summary: 'Aadhaar re-verified, address updated in CBS.',
    },
    {
        id: 'sess-004', customer: 'Vikram Mehta', cif: 'PUN-00356712', staff: 'Sneha Joshi',
        branch: 'Pune Koregaon Park', token: 'Q-17', intent: 'complaint', urgency: 'high',
        emotion: 'frustrated', status: 'closed', duration: '15m 31s',
        created_at: '2026-03-10T13:20:00', summary: 'UPI transaction dispute raised, escalated to fraud team.',
    },
    {
        id: 'sess-005', customer: 'Meena Deshpande', cif: 'PUN-00401289', staff: 'Amit Desai',
        branch: 'Pune Koregaon Park', token: 'Q-18', intent: 'fd_query', urgency: 'low',
        emotion: 'calm', status: 'active', duration: '—',
        created_at: '2026-03-10T14:50:00', summary: null,
    },
]

const SENTIMENT_CHART_DATA = [
    { time: '09:00', stress: 0.78, sessions: 1 },
    { time: '10:00', stress: 0.32, sessions: 1 },
    { time: '11:00', stress: 0.15, sessions: 1 },
    { time: '12:00', stress: 0.0, sessions: 0 },
    { time: '13:00', stress: 0.61, sessions: 1 },
    { time: '14:00', stress: 0.18, sessions: 1 },
]

const INTENT_STATS = [
    { name: 'Lost Card', count: 4, color: '#ff3355' },
    { name: 'Loan Query', count: 7, color: '#3b82f6' },
    { name: 'KYC Update', count: 5, color: '#22c55e' },
    { name: 'Complaint', count: 3, color: '#f59e0b' },
    { name: 'FD Query', count: 6, color: '#8b5cf6' },
    { name: 'Balance', count: 12, color: '#06b6d4' },
]

// ── Urgency / Status badges ────────────────────────────
const URGENCY = {
    critical: 'bg-critical/15 text-critical border-critical/30',
    high: 'bg-warn/15 text-warn border-warn/30',
    medium: 'bg-gold/15 text-gold border-gold/30',
    low: 'bg-accent/15 text-accent border-accent/30',
}

const STATUS = {
    active: 'bg-accent2/15 text-accent2 border-accent2/30',
    closed: 'bg-surface2 text-muted border-border',
}

// ── Page ────────────────────────────────────────────────
export default function ReportsPage() {
    const [sessions] = useState(DEMO_SESSIONS)

    return (
        <div className="flex flex-col h-screen bg-bg overflow-hidden">
            <Header />

            <div className="flex-1 overflow-y-auto">
                {/* Stats row */}
                <div className="grid grid-cols-4 gap-4 px-6 pt-6 pb-4">
                    <StatCard label="Today's Sessions" value={sessions.length} icon="🎟" accent="text-accent" />
                    <StatCard label="Avg Stress Level" value="42%" icon="🧠" accent="text-warn" />
                    <StatCard label="Compliance Score" value="98%" icon="✅" accent="text-accent2" />
                    <StatCard label="Avg Duration" value="8m 19s" icon="⏱" accent="text-gold" />
                </div>

                {/* Charts row */}
                <div className="grid grid-cols-2 gap-4 px-6 pb-4">
                    {/* Stress trend */}
                    <div className="bg-surface2 border border-border rounded-xl p-4">
                        <div className="text-[11px] font-syne font-bold text-muted uppercase tracking-widest mb-3">
                            🧠 Stress Trend (Today)
                        </div>
                        <div className="h-40">
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={SENTIMENT_CHART_DATA}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#1e2333" />
                                    <XAxis dataKey="time" tick={{ fill: '#636b8a', fontSize: 11 }} />
                                    <YAxis tick={{ fill: '#636b8a', fontSize: 11 }} domain={[0, 1]} />
                                    <Tooltip
                                        contentStyle={{ background: '#0e1118', border: '1px solid #1e2333', fontSize: 11 }}
                                        formatter={v => [`${Math.round(v * 100)}%`, 'Stress']}
                                    />
                                    <Line type="monotone" dataKey="stress" stroke="#ff3355" strokeWidth={2} dot={{ fill: '#ff3355', r: 3 }} />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Intent distribution */}
                    <div className="bg-surface2 border border-border rounded-xl p-4">
                        <div className="text-[11px] font-syne font-bold text-muted uppercase tracking-widest mb-3">
                            💡 Intent Distribution (This Week)
                        </div>
                        <div className="h-40">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={INTENT_STATS}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#1e2333" />
                                    <XAxis dataKey="name" tick={{ fill: '#636b8a', fontSize: 10 }} />
                                    <YAxis tick={{ fill: '#636b8a', fontSize: 11 }} />
                                    <Tooltip contentStyle={{ background: '#0e1118', border: '1px solid #1e2333', fontSize: 11 }} />
                                    <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                </div>

                {/* Session table */}
                <div className="px-6 pb-6">
                    <div className="bg-surface2 border border-border rounded-xl overflow-hidden">
                        <div className="px-4 py-3 border-b border-border flex items-center justify-between">
                            <div className="text-[11px] font-syne font-bold text-muted uppercase tracking-widest">
                                🎟 Session History — {dayjs().format('DD MMM YYYY')}
                            </div>
                            <div className="text-xs text-muted">{sessions.length} sessions</div>
                        </div>

                        <table className="w-full text-xs">
                            <thead>
                                <tr className="border-b border-border text-muted text-[10px] uppercase tracking-wider">
                                    <th className="text-left px-4 py-2.5 font-semibold">Token</th>
                                    <th className="text-left px-4 py-2.5 font-semibold">Customer</th>
                                    <th className="text-left px-4 py-2.5 font-semibold">Intent</th>
                                    <th className="text-left px-4 py-2.5 font-semibold">Urgency</th>
                                    <th className="text-left px-4 py-2.5 font-semibold">Emotion</th>
                                    <th className="text-left px-4 py-2.5 font-semibold">Duration</th>
                                    <th className="text-left px-4 py-2.5 font-semibold">Status</th>
                                    <th className="text-left px-4 py-2.5 font-semibold">Summary</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-border">
                                {sessions.map((s, i) => (
                                    <motion.tr
                                        key={s.id}
                                        initial={{ opacity: 0, y: 8 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{ delay: i * 0.05 }}
                                        className="hover:bg-surface transition-colors"
                                    >
                                        <td className="px-4 py-3 font-mono font-bold text-accent">{s.token}</td>
                                        <td className="px-4 py-3">
                                            <div className="font-semibold text-text">{s.customer}</div>
                                            <div className="text-muted text-[10px] font-mono">CIF #{s.cif}</div>
                                        </td>
                                        <td className="px-4 py-3 font-mono">{s.intent?.replace('_', ' ').toUpperCase()}</td>
                                        <td className="px-4 py-3">
                                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase border ${URGENCY[s.urgency]}`}>
                                                {s.urgency}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3 capitalize">{s.emotion}</td>
                                        <td className="px-4 py-3 font-mono text-muted">{s.duration}</td>
                                        <td className="px-4 py-3">
                                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase border ${STATUS[s.status]}`}>
                                                {s.status}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3 max-w-[200px] truncate text-muted">
                                            {s.summary || '—'}
                                        </td>
                                    </motion.tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    )
}

function StatCard({ label, value, icon, accent }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-surface2 border border-border rounded-xl p-4 flex items-center gap-3"
        >
            <div className="text-2xl">{icon}</div>
            <div>
                <div className={`font-syne font-extrabold text-xl ${accent}`}>{value}</div>
                <div className="text-[10px] text-muted uppercase tracking-wide">{label}</div>
            </div>
        </motion.div>
    )
}
