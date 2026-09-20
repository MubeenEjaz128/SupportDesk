import React from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import Layout from './components/Layout'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Tickets from './pages/Tickets'
import TicketDetail from './pages/TicketDetail'
import Customers from './pages/Customers'
import Knowledge from './pages/Knowledge'
import ActivityPage from './pages/ActivityPage'
import Team from './pages/Team'
import Profile from './pages/Profile'

function Guard({ children, roles }) {
  const { user } = useAuth()
  if (!user) return <Navigate to="/login" replace />
  if (roles && !roles.includes(user.role)) return <Navigate to="/" replace />
  return children
}

function PublicOnly({ children }) {
  const { user } = useAuth()
  return user ? <Navigate to="/" replace /> : children
}

function Shell({ children, roles }) {
  return (
    <Guard roles={roles}>
      <Layout>{children}</Layout>
    </Guard>
  )
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<PublicOnly><Login /></PublicOnly>} />
      <Route path="/register" element={<PublicOnly><Register /></PublicOnly>} />

      <Route path="/" element={<Shell><Dashboard /></Shell>} />
      <Route path="/tickets" element={<Shell><Tickets /></Shell>} />
      <Route path="/tickets/:id" element={<Shell><TicketDetail /></Shell>} />
      <Route path="/knowledge" element={<Shell><Knowledge /></Shell>} />

      <Route
        path="/customers"
        element={<Shell roles={['admin', 'supervisor', 'agent']}><Customers /></Shell>}
      />
      <Route
        path="/activity"
        element={<Shell roles={['admin', 'supervisor']}><ActivityPage /></Shell>}
      />
      <Route
        path="/team"
        element={<Shell roles={['admin', 'supervisor']}><Team /></Shell>}
      />
      <Route
        path="/profile"
        element={<Shell roles={['customer']}><Profile /></Shell>}
      />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
