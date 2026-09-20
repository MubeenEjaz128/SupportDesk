import React, { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  ArrowLeft,
  Bot,
  MessageSquare,
  Send,
  StickyNote,
  UserCheck,
  XCircle,
} from 'lucide-react'
import { api } from '../lib/api'
import { Badge, Loader, toneForPriority, toneForStatus } from '../components/UI'
import { useAuth } from '../context/AuthContext'

export default function TicketDetail() {
  const { id } = useParams()
  const { user } = useAuth()
  const isCustomer = user?.role === 'customer'

  const [ticket, setTicket] = useState(null)
  const [body, setBody] = useState('')
  const [internal, setInternal] = useState(false)
  const [ai, setAi] = useState(false)
  const [error, setError] = useState('')
  const [sending, setSending] = useState(false)

  const load = () => {
    api(`/tickets/${id}/`)
      .then(setTicket)
      .catch((e) => setError(e.message))
  }

  useEffect(load, [id])

  const send = async () => {
    if (!body.trim()) return
    setSending(true)
    setError('')
    try {
      await api(`/tickets/${id}/messages/`, {
        method: 'POST',
        body: JSON.stringify({
          body,
          is_internal: isCustomer ? false : internal,
          is_ai_generated: isCustomer ? false : ai,
        }),
      })
      setBody('')
      setAi(false)
      setInternal(false)
      await load()
    } catch (e) {
      setError(e.message)
    } finally {
      setSending(false)
    }
  }

  const suggest = async () => {
    setSending(true)
    setError('')
    try {
      const data = await api(`/tickets/${id}/ai-suggest/`, {
        method: 'POST',
        body: '{}',
      })
      setBody(data.reply)
      setAi(data.provider !== 'fallback' && data.provider !== 'error')
    } catch (e) {
      setError(e.message)
    } finally {
      setSending(false)
    }
  }

  const action = async (name) => {
    setSending(true)
    setError('')
    try {
      await api(`/tickets/${id}/${name}/`, { method: 'POST', body: '{}' })
      await load()
    } catch (e) {
      setError(e.message)
    } finally {
      setSending(false)
    }
  }

  const patch = async (data) => {
    setError('')
    try {
      await api(`/tickets/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      })
      await load()
    } catch (e) {
      setError(e.message)
    }
  }

  if (!ticket && !error) return <Loader label="Opening ticket..." />
  if (error && !ticket) return <div className="error-box">{error}</div>

  return (
    <>
      <Link to="/tickets" className="back-link">
        <ArrowLeft size={17} />Back to {isCustomer ? 'my tickets' : 'tickets'}
      </Link>

      <div className="ticket-detail-head">
        <div>
          <div className="ticket-meta">
            <span>{ticket.ticket_number}</span>
            <Badge tone={toneForStatus(ticket.status)}>{ticket.status}</Badge>
            <Badge tone={toneForPriority(ticket.priority)}>{ticket.priority}</Badge>
          </div>
          <h1>{ticket.subject}</h1>
          <p>
            {isCustomer
              ? `Opened ${new Date(ticket.created_at).toLocaleString()}`
              : <>Customer: <strong>{ticket.customer?.name}</strong> · {ticket.customer?.email || 'No email'}</>}
          </p>
        </div>

        {!isCustomer && (
          <div className="detail-actions">
            <button className="btn" onClick={() => action('assign-to-me')} disabled={sending}>
              <UserCheck size={17} />Assign to me
            </button>
            <button className="btn" onClick={() => action('close')} disabled={sending}>
              <XCircle size={17} />Close
            </button>
          </div>
        )}
      </div>

      {error && <div className="error-box">{error}</div>}

      <div className="ticket-layout">
        <section className="conversation panel">
          <div className="initial-message">
            <span>Original request</span>
            <p>{ticket.description}</p>
          </div>

          <div className="message-list">
            {ticket.messages?.map((message) => (
              <article
                className={`message ${message.is_internal ? 'internal' : ''}`}
                key={message.id}
              >
                <div className="message-head">
                  <div className="avatar small">
                    {(message.author_name || message.author_username || 'C')[0].toUpperCase()}
                  </div>
                  <div>
                    <strong>{message.author_name || message.author_username || ticket.customer.name}</strong>
                    <span>{new Date(message.created_at).toLocaleString()}</span>
                  </div>
                  {message.is_internal && <Badge tone="amber">Internal note</Badge>}
                  {!isCustomer && message.is_ai_generated && <Badge tone="purple">AI assisted</Badge>}
                </div>
                <p>{message.body}</p>
              </article>
            ))}
          </div>

          {ticket.status !== 'closed' ? (
            <div className="composer">
              {!isCustomer && (
                <div className="composer-tabs">
                  <button
                    className={!internal ? 'active' : ''}
                    onClick={() => setInternal(false)}
                    type="button"
                  >
                    <MessageSquare size={16} />Reply
                  </button>
                  <button
                    className={internal ? 'active' : ''}
                    onClick={() => setInternal(true)}
                    type="button"
                  >
                    <StickyNote size={16} />Internal note
                  </button>
                </div>
              )}

              {isCustomer && (
                <div className="composer-label">
                  <MessageSquare size={16} />Reply to support
                </div>
              )}

              <textarea
                rows="6"
                value={body}
                onChange={(e) => {
                  setBody(e.target.value)
                  setAi(false)
                }}
                placeholder={
                  isCustomer
                    ? 'Add more information or reply to the support team...'
                    : internal
                      ? 'Write a private note for your team...'
                      : 'Write a reply to the customer...'
                }
              />

              <div className="composer-actions">
                {!isCustomer && !internal && (
                  <button className="btn ai" onClick={suggest} disabled={sending}>
                    <Bot size={17} />Suggest with AI
                  </button>
                )}
                <button
                  className="btn primary composer-send"
                  onClick={send}
                  disabled={sending || !body.trim()}
                >
                  <Send size={17} />
                  {sending ? 'Working...' : internal ? 'Add note' : 'Send reply'}
                </button>
              </div>
            </div>
          ) : (
            <div className="closed-notice">This ticket is closed. Contact support if you need it reopened.</div>
          )}
        </section>

        <aside className="ticket-side">
          <section className="panel">
            <h3>Ticket details</h3>

            {!isCustomer ? (
              <>
                <label className="field">
                  <span>Status</span>
                  <select value={ticket.status} onChange={(e) => patch({ status: e.target.value })}>
                    <option value="open">Open</option>
                    <option value="pending">Pending</option>
                    <option value="resolved">Resolved</option>
                    <option value="closed">Closed</option>
                  </select>
                </label>
                <label className="field">
                  <span>Priority</span>
                  <select value={ticket.priority} onChange={(e) => patch({ priority: e.target.value })}>
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="urgent">Urgent</option>
                  </select>
                </label>
              </>
            ) : (
              <div className="detail-badges">
                <div><span>Status</span><Badge tone={toneForStatus(ticket.status)}>{ticket.status}</Badge></div>
                <div><span>Priority</span><Badge tone={toneForPriority(ticket.priority)}>{ticket.priority}</Badge></div>
              </div>
            )}

            <div className="meta-list">
              <div><span>Assignee</span><strong>{ticket.assigned_to_username || 'Support queue'}</strong></div>
              <div><span>Category</span><strong>{ticket.category || 'General'}</strong></div>
              <div><span>Source</span><strong>{ticket.source}</strong></div>
              <div><span>Created</span><strong>{new Date(ticket.created_at).toLocaleDateString()}</strong></div>
            </div>
          </section>

          {!isCustomer && (
            <section className="panel">
              <h3>Customer</h3>
              <div className="customer-card">
                <div className="avatar large">{ticket.customer.name[0]}</div>
                <strong>{ticket.customer.name}</strong>
                <span>{ticket.customer.company || 'Individual customer'}</span>
                <a href={`mailto:${ticket.customer.email}`}>{ticket.customer.email}</a>
                <span>{ticket.customer.phone}</span>
              </div>
            </section>
          )}
        </aside>
      </div>
    </>
  )
}
