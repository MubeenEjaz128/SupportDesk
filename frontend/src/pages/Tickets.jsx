import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Filter, Plus, Search } from 'lucide-react'
import { api } from '../lib/api'
import {
  Badge,
  Empty,
  Field,
  Loader,
  Modal,
  PageHeader,
  toneForPriority,
  toneForStatus,
} from '../components/UI'
import { useAuth } from '../context/AuthContext'

const staffBlank = {
  subject: '',
  description: '',
  customer_id: '',
  priority: 'medium',
  status: 'open',
  source: 'web',
  category: '',
  tags: '',
}

const customerBlank = {
  subject: '',
  description: '',
  category: '',
}

export default function Tickets() {
  const { user } = useAuth()
  const isCustomer = user?.role === 'customer'

  const [items, setItems] = useState([])
  const [customers, setCustomers] = useState([])
  const [loading, setLoading] = useState(true)
  const [q, setQ] = useState('')
  const [status, setStatus] = useState('')
  const [priority, setPriority] = useState('')
  const [open, setOpen] = useState(false)
  const [form, setForm] = useState(isCustomer ? customerBlank : staffBlank)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const load = () => {
    setLoading(true)
    const params = new URLSearchParams()
    if (q) params.set('search', q)
    if (status) params.set('status', status)
    if (priority) params.set('priority', priority)

    api(`/tickets/?${params}`)
      .then((data) => setItems(data.results || data))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    if (!isCustomer) {
      api('/customers/')
        .then((data) => setCustomers(data.results || data))
        .catch(() => {})
    }
  }, [isCustomer])

  useEffect(() => {
    const timer = setTimeout(load, 250)
    return () => clearTimeout(timer)
  }, [q, status, priority])

  const create = async (e) => {
    e.preventDefault()
    setSaving(true)
    setError('')

    try {
      const payload = isCustomer
        ? form
        : {
            ...form,
            tags: form.tags.split(',').map((x) => x.trim()).filter(Boolean),
          }

      await api('/tickets/', {
        method: 'POST',
        body: JSON.stringify(payload),
      })

      setOpen(false)
      setForm(isCustomer ? customerBlank : staffBlank)
      load()
    } catch (e) {
      setError(e.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <>
      <PageHeader
        title={isCustomer ? 'My Tickets' : 'Tickets'}
        subtitle={
          isCustomer
            ? 'Open a request and keep track of every reply from the support team.'
            : 'Search, prioritize and resolve customer conversations.'
        }
        action={
          <button className="btn primary" onClick={() => setOpen(true)}>
            <Plus size={17} />{isCustomer ? 'New request' : 'New ticket'}
          </button>
        }
      />

      {error && <div className="error-box">{error}</div>}

      <div className="toolbar">
        <div className="searchbox">
          <Search size={17} />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder={isCustomer ? 'Search my tickets...' : 'Search ticket, subject or customer...'}
          />
        </div>

        <div className="filter-group">
          <Filter size={17} />
          <select value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="">All statuses</option>
            <option value="open">Open</option>
            <option value="pending">Pending</option>
            <option value="resolved">Resolved</option>
            <option value="closed">Closed</option>
          </select>
          <select value={priority} onChange={(e) => setPriority(e.target.value)}>
            <option value="">All priorities</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="urgent">Urgent</option>
          </select>
        </div>
      </div>

      <section className="panel no-pad">
        {loading ? (
          <Loader />
        ) : items.length === 0 ? (
          <Empty
            title={isCustomer ? 'No support requests yet' : 'No matching tickets'}
            text={
              isCustomer
                ? 'Create your first ticket when you need help.'
                : 'Adjust filters or create a new support ticket.'
            }
          />
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Ticket</th>
                  {!isCustomer && <th>Customer</th>}
                  {!isCustomer && <th>Assignee</th>}
                  <th>Status</th>
                  <th>Priority</th>
                  {!isCustomer && <th>Source</th>}
                  <th>Updated</th>
                </tr>
              </thead>
              <tbody>
                {items.map((ticket) => (
                  <tr key={ticket.id}>
                    <td>
                      <Link className="ticket-link" to={`/tickets/${ticket.id}`}>
                        <strong>{ticket.ticket_number}</strong>
                        <span>{ticket.subject}</span>
                      </Link>
                    </td>
                    {!isCustomer && (
                      <td>
                        <strong>{ticket.customer?.name}</strong>
                        <small>{ticket.customer?.email}</small>
                      </td>
                    )}
                    {!isCustomer && (
                      <td>{ticket.assigned_to_username || <span className="muted">Unassigned</span>}</td>
                    )}
                    <td><Badge tone={toneForStatus(ticket.status)}>{ticket.status}</Badge></td>
                    <td><Badge tone={toneForPriority(ticket.priority)}>{ticket.priority}</Badge></td>
                    {!isCustomer && <td>{ticket.source}</td>}
                    <td>{new Date(ticket.updated_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <Modal
        open={open}
        onClose={() => setOpen(false)}
        title={isCustomer ? 'Open a support request' : 'Create ticket'}
        wide
      >
        <form className="form-grid" onSubmit={create}>
          <Field label="Subject">
            <input
              required
              value={form.subject}
              onChange={(e) => setForm({ ...form, subject: e.target.value })}
              placeholder="Briefly describe the issue"
            />
          </Field>

          {!isCustomer && (
            <Field label="Customer">
              <select
                required
                value={form.customer_id}
                onChange={(e) => setForm({ ...form, customer_id: e.target.value })}
              >
                <option value="">Select customer</option>
                {customers.map((customer) => (
                  <option value={customer.id} key={customer.id}>
                    {customer.name}{customer.email ? ` (${customer.email})` : ''}
                  </option>
                ))}
              </select>
            </Field>
          )}

          {!isCustomer && (
            <Field label="Priority">
              <select
                value={form.priority}
                onChange={(e) => setForm({ ...form, priority: e.target.value })}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
            </Field>
          )}

          {!isCustomer && (
            <Field label="Source">
              <select
                value={form.source}
                onChange={(e) => setForm({ ...form, source: e.target.value })}
              >
                <option value="web">Web</option>
                <option value="email">Email</option>
                <option value="phone">Phone</option>
                <option value="chat">Chat</option>
                <option value="social">Social</option>
              </select>
            </Field>
          )}

          <Field label="Category">
            <input
              value={form.category}
              onChange={(e) => setForm({ ...form, category: e.target.value })}
              placeholder="Billing, account, technical..."
            />
          </Field>

          {!isCustomer && (
            <Field label="Tags">
              <input
                value={form.tags}
                onChange={(e) => setForm({ ...form, tags: e.target.value })}
                placeholder="billing, login"
              />
            </Field>
          )}

          <Field label="Description">
            <textarea
              required
              rows="7"
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              placeholder="Include the details needed to understand the issue."
            />
          </Field>

          <div className="form-actions">
            <button type="button" className="btn" onClick={() => setOpen(false)}>Cancel</button>
            <button className="btn primary" disabled={saving}>
              {saving ? 'Creating...' : isCustomer ? 'Submit request' : 'Create ticket'}
            </button>
          </div>
        </form>
      </Modal>
    </>
  )
}
