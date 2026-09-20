import React, { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard,
  Ticket,
  Users,
  BookOpen,
  Activity,
  UserCog,
  CircleUserRound,
  LogOut,
  Menu,
  X,
  Sparkles,
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'

const staffBase = [
  ['/', 'Dashboard', LayoutDashboard],
  ['/tickets', 'Tickets', Ticket],
  ['/customers', 'Customers', Users],
  ['/knowledge', 'Knowledge Base', BookOpen],
]

const customerNav = [
  ['/', 'Dashboard', LayoutDashboard],
  ['/tickets', 'My Tickets', Ticket],
  ['/knowledge', 'Help Center', BookOpen],
  ['/profile', 'My Profile', CircleUserRound],
]

export default function Layout({ children }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)

  const doLogout = () => {
    logout()
    navigate('/login')
  }

  let items = customerNav
  if (user?.role === 'agent') items = staffBase
  if (['admin', 'supervisor'].includes(user?.role)) {
    items = [
      ...staffBase,
      ['/activity', 'Activity', Activity],
      ['/team', 'Team', UserCog],
    ]
  }

  const workspaceLabel =
    user?.role === 'customer' ? 'Customer Portal' : 'Support Workspace'

  return (
    <div className="app-shell">
      <aside className={`sidebar ${open ? 'sidebar-open' : ''}`}>
        <div className="brand">
          <div className="brand-mark"><Sparkles size={20} /></div>
          <div>
            <strong>SupportDesk</strong>
            <span>{workspaceLabel}</span>
          </div>
          <button className="mobile-close" onClick={() => setOpen(false)}><X /></button>
        </div>

        <nav>
          {items.map(([to, label, Icon]) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              onClick={() => setOpen(false)}
              className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
            >
              <Icon size={19} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="side-user">
          <div className="avatar">
            {(user?.display_name || user?.username || 'U').slice(0, 1).toUpperCase()}
          </div>
          <div className="side-user-text">
            <strong>{user?.display_name || user?.username}</strong>
            <span>{user?.role}</span>
          </div>
          <button className="icon-btn dark" title="Log out" onClick={doLogout}>
            <LogOut size={18} />
          </button>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <button className="mobile-menu" onClick={() => setOpen(true)}><Menu /></button>
          <div className="top-title">
            {user?.role === 'customer' ? 'Your Support Center' : 'Customer Support Operations'}
          </div>
          <div className="top-chip"><span className="online-dot" />API connected</div>
        </header>
        <div className="content">{children}</div>
      </main>
    </div>
  )
}
