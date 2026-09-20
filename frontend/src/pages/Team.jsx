import React, { useEffect, useState } from 'react'
import { Plus, UserCheck, UserX } from 'lucide-react'
import { api } from '../lib/api'
import { useAuth } from '../context/AuthContext'
import { Badge, Field, Loader, Modal, PageHeader } from '../components/UI'

const blank = {
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  display_name: '',
  role: 'agent',
  password: '',
}

export default function Team() {
  const { user } = useAuth()
  const isAdmin = user?.role === 'admin'

  const [items, setItems] = useState(null)
  const [error, setError] = useState('')
  const [open, setOpen] = useState(false)
  const [form, setForm] = useState(blank)
  const [saving, setSaving] = useState(false)

  const load = () => {
    api('/team/')
      .then((data) => setItems(data.results || data))
      .catch((e) => setError(e.message))
  }

  useEffect(load, [])

  const create = async (e) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    try {
      await api('/team/', {
        method: 'POST',
        body: JSON.stringify(form),
      })
      setOpen(false)
      setForm(blank)
      load()
    } catch (e) {
      setError(e.message)
    } finally {
      setSaving(false)
    }
  }

  const setRole = async (member, role) => {
    try {
      await api(`/team/${member.username}/role/`, {
        method: 'PATCH',
        body: JSON.stringify({ role }),
      })
      load()
    } catch (e) {
      setError(e.message)
    }
  }

  const setActive = async (member, active) => {
    try {
      await api(`/team/${member.username}/${active ? 'activate' : 'deactivate'}/`, {
        method: 'POST',
        body: '{}',
      })
      load()
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <>
      <PageHeader
        title="Team"
        subtitle="Support staff, access level and account status."
        action={
          isAdmin
            ? <button className="btn primary" onClick={() => setOpen(true)}><Plus size={17} />Add team member</button>
            : null
        }
      />

      {error && <div className="error-box">{error}</div>}

      {!items ? (
        <Loader />
      ) : (
        <div className="team-grid">
          {items.map((member) => (
            <div className={`team-card ${!member.is_active ? 'team-card-disabled' : ''}`} key={member.username}>
              <div className="avatar large">
                {(member.display_name || member.username)[0].toUpperCase()}
              </div>

              <div className="team-main">
                <h3>{member.display_name || member.username}</h3>
                <p>@{member.username} · {member.email || 'No email'}</p>
                <div className="member-badges">
                  <Badge tone={member.role === 'admin' ? 'purple' : member.role === 'supervisor' ? 'blue' : 'gray'}>
                    {member.role}
                  </Badge>
                  {!member.is_active && <Badge tone="red">inactive</Badge>}
                </div>
              </div>

              {isAdmin && member.username !== user.username && (
                <div className="team-controls">
                  <select value={member.role} onChange={(e) => setRole(member, e.target.value)}>
                    <option value="agent">agent</option>
                    <option value="supervisor">supervisor</option>
                    <option value="admin">admin</option>
                  </select>
                  <button
                    className="icon-btn"
                    title={member.is_active ? 'Deactivate account' : 'Activate account'}
                    onClick={() => setActive(member, !member.is_active)}
                  >
                    {member.is_active ? <UserX size={16} /> : <UserCheck size={16} />}
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <Modal open={open} onClose={() => setOpen(false)} title="Add team member">
        <form className="form-grid" onSubmit={create}>
          <Field label="Username">
            <input required value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
          </Field>
          <Field label="Email">
            <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          </Field>
          <Field label="First name">
            <input value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} />
          </Field>
          <Field label="Last name">
            <input value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} />
          </Field>
          <Field label="Display name">
            <input value={form.display_name} onChange={(e) => setForm({ ...form, display_name: e.target.value })} />
          </Field>
          <Field label="Role">
            <select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
              <option value="agent">Agent</option>
              <option value="supervisor">Supervisor</option>
            </select>
          </Field>
          <Field label="Temporary password">
            <input
              required
              minLength="8"
              type="password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
            />
          </Field>
          <div className="form-actions">
            <button type="button" className="btn" onClick={() => setOpen(false)}>Cancel</button>
            <button className="btn primary" disabled={saving}>
              {saving ? 'Creating...' : 'Create account'}
            </button>
          </div>
        </form>
      </Modal>
    </>
  )
}
