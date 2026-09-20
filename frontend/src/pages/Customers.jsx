import React, { useEffect, useState } from 'react'
import { Plus, Search } from 'lucide-react'
import { api } from '../lib/api'
import { Empty, Field, Loader, Modal, PageHeader } from '../components/UI'
import { useAuth } from '../context/AuthContext'

const blank = { name: '', email: '', phone: '', company: '', notes: '', tags: '' }

export default function Customers() {
  const { user } = useAuth()
  const canManage = ['admin', 'supervisor'].includes(user?.role)

  const [items, setItems] = useState([])
  const [q, setQ] = useState('')
  const [loading, setLoading] = useState(true)
  const [open, setOpen] = useState(false)
  const [form, setForm] = useState(blank)
  const [error, setError] = useState('')

  const load = () => {
    setLoading(true)
    api(`/customers/?search=${encodeURIComponent(q)}`)
      .then((data) => setItems(data.results || data))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    const timer = setTimeout(load, 250)
    return () => clearTimeout(timer)
  }, [q])

  const save = async (e) => {
    e.preventDefault()
    try {
      await api('/customers/', {
        method: 'POST',
        body: JSON.stringify({
          ...form,
          tags: form.tags.split(',').map((x) => x.trim()).filter(Boolean),
        }),
      })
      setOpen(false)
      setForm(blank)
      load()
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <>
      <PageHeader
        title="Customers"
        subtitle={
          canManage
            ? 'Customer directory, contact information and support history.'
            : 'Customer records connected to the support queue.'
        }
        action={
          canManage
            ? <button className="btn primary" onClick={() => setOpen(true)}><Plus size={17} />Add customer</button>
            : null
        }
      />

      {error && <div className="error-box">{error}</div>}

      <div className="toolbar">
        <div className="searchbox">
          <Search size={17} />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search name, email, phone, company..."
          />
        </div>
      </div>

      <section className="panel no-pad">
        {loading ? (
          <Loader />
        ) : items.length === 0 ? (
          <Empty />
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Customer</th>
                  <th>Company</th>
                  <th>Phone</th>
                  <th>Tickets</th>
                  <th>Tags</th>
                  <th>Added</th>
                </tr>
              </thead>
              <tbody>
                {items.map((customer) => (
                  <tr key={customer.id}>
                    <td>
                      <strong>{customer.name}</strong>
                      <small>{customer.email}</small>
                    </td>
                    <td>{customer.company || '—'}</td>
                    <td>{customer.phone || '—'}</td>
                    <td><strong>{customer.ticket_count}</strong></td>
                    <td>
                      <div className="tag-list">
                        {(customer.tags || []).map((tag) => <span className="tag" key={tag}>{tag}</span>)}
                      </div>
                    </td>
                    <td>{new Date(customer.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <Modal open={open} onClose={() => setOpen(false)} title="Add customer">
        <form className="form-grid" onSubmit={save}>
          <Field label="Full name">
            <input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          </Field>
          <Field label="Email">
            <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          </Field>
          <Field label="Phone">
            <input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
          </Field>
          <Field label="Company">
            <input value={form.company} onChange={(e) => setForm({ ...form, company: e.target.value })} />
          </Field>
          <Field label="Tags">
            <input value={form.tags} onChange={(e) => setForm({ ...form, tags: e.target.value })} placeholder="vip, enterprise" />
          </Field>
          <Field label="Notes">
            <textarea rows="4" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
          </Field>
          <div className="form-actions">
            <button type="button" className="btn" onClick={() => setOpen(false)}>Cancel</button>
            <button className="btn primary">Save customer</button>
          </div>
        </form>
      </Modal>
    </>
  )
}
