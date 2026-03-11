import { Routes, Route, Navigate } from 'react-router-dom'
import Dashboard from '@/pages/index'
import SessionPage from '@/pages/session/[id]'
import ReportsPage from '@/pages/reports'

export default function App() {
  return (
    <Routes>
      <Route path="/"              element={<Dashboard />} />
      <Route path="/session/:id"   element={<SessionPage />} />
      <Route path="/reports"       element={<ReportsPage />} />
      <Route path="*"              element={<Navigate to="/" replace />} />
    </Routes>
  )
}