import React, { useEffect, useState } from 'react'
import { Ticket, Clock3, CheckCircle2, Users, Inbox, ArrowUpRight } from 'lucide-react'
import { Link } from 'react-router-dom'
import { api } from '../lib/api'
import { Badge, Loader, PageHeader, toneForPriority, toneForStatus } from '../components/UI'
import { useAuth } from '../context/AuthContext'

export default function Dashboard() {
  const { user } = useAuth()
  const [data, setData] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api('/dashboard/stats/').then(setData).catch((e) => setError(e.message))
  }, [])

  if (!data && !error) return <Loader label="Loading support metrics..." />
  if (error) return <div className="error-box">{error}</div>

  const customer = user?.role === 'customer'
  const cards = customer
    ? [
        ['My tickets', data.total_tickets, Ticket],
        ['Open', data.open_tickets, Inbox],
        ['Pending', data.pending_tickets, Clock3],
        ['Resolved', data.resolved_tickets, CheckCircle2],
      ]
    : [
        ['Total tickets', data.total_tickets, Ticket],
        ['Open', data.open_tickets, Inbox],
        ['Pending', data.pending_tickets, Clock3],
        ['Resolved', data.resolved_tickets, CheckCircle2],
        ['Customers', data.customers, Users],
      ]

  const max = Math.max(1, ...Object.values(data.by_priority || {}))

  return (
    <>
      <PageHeader
        title={customer ? 'My Support' : 'Dashboard'}
        subtitle={
          customer
            ? 'Track your requests and continue conversations with the support team.'
            : 'A live snapshot of customer support operations.'
        }
        action={
          customer
            ? <Link className="btn primary" to="/tickets">Open a support ticket</Link>
            : null
        }
      />

      <div className={`stat-grid ${customer ? 'customer-stat-grid' : ''}`}>
        {cards.map(([label, value, Icon]) => (
          <div className="stat-card" key={label}>
            <div className="stat-icon"><Icon size={20} /></div>
            <div><span>{label}</span><strong>{value}</strong></div>
          </div>
        ))}
      </div>

      <div className="dashboard-grid">
        {!customer && (
          <section className="panel">
            <div className="panel-head">
              <div><h2>Ticket priority</h2><p>Current workload distribution</p></div>
            </div>
            <div className="bars">
              {Object.entries(data.by_priority || {}).map(([key, value]) => (
                <div className="bar-row" key={key}>
                  <span className="bar-label">{key}</span>
                  <div className="bar-track">
                    <div
                      className={`bar-fill bar-${toneForPriority(key)}`}
                      style={{ width: `${Math.max(4, value / max * 100)}%` }}
                    />
                  </div>
                  <strong>{value}</strong>
                </div>
              ))}
            </div>
            <div className="mini-kpi">
              <span>{user.role === 'agent' ? 'Assigned to you and active' : 'Your active tickets'}</span>
              <strong>{data.my_open_tickets}</strong>
            </div>
          </section>
        )}

        <section className={`panel ${customer ? 'customer-recent' : 'span-2'}`}>
          <div className="panel-head">
            <div>
              <h2>{customer ? 'Recent requests' : 'Recent tickets'}</h2>
              <p>{customer ? 'Your latest support conversations' : 'Most recently updated conversations'}</p>
            </div>
            <Link className="text-link" to="/tickets">View all <ArrowUpRight size={15} /></Link>
          </div>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Ticket</th>
                  {!customer && <th>Customer</th>}
                  <th>Status</th>
                  <th>Priority</th>
                  <th>Updated</th>
                </tr>
              </thead>
              <tbody>
                {data.recent_tickets.map((ticket) => (
                  <tr key={ticket.id}>
                    <td>
                      <Link className="ticket-link" to={`/tickets/${ticket.id}`}>
                        <strong>{ticket.ticket_number}</strong>
                        <span>{ticket.subject}</span>
                      </Link>
                    </td>
                    {!customer && <td>{ticket.customer?.name}</td>}
                    <td><Badge tone={toneForStatus(ticket.status)}>{ticket.status}</Badge></td>
                    <td><Badge tone={toneForPriority(ticket.priority)}>{ticket.priority}</Badge></td>
                    <td>{new Date(ticket.updated_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </>
  )
}
