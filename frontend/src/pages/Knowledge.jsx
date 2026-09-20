import React, { useEffect, useState } from 'react'
import { BookOpen, Plus, Search } from 'lucide-react'
import { api } from '../lib/api'
import { Empty, Field, Loader, Modal, PageHeader } from '../components/UI'
import { useAuth } from '../context/AuthContext'

const blank = { title: '', category: '', content: '', is_published: true }

export default function Knowledge() {
  const { user } = useAuth()
  const canManage = ['admin', 'supervisor'].includes(user?.role)
  const isCustomer = user?.role === 'customer'

  const [items, setItems] = useState([])
  const [q, setQ] = useState('')
  const [loading, setLoading] = useState(true)
  const [open, setOpen] = useState(false)
  const [form, setForm] = useState(blank)
  const [selected, setSelected] = useState(null)
  const [error, setError] = useState('')

  const load = () => {
    setLoading(true)
    api(`/knowledge/?search=${encodeURIComponent(q)}`)
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
      await api('/knowledge/', {
        method: 'POST',
        body: JSON.stringify(form),
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
        title={isCustomer ? 'Help Center' : 'Knowledge Base'}
        subtitle={
          isCustomer
            ? 'Browse support guides before or while you work with the support team.'
            : 'Reusable support guidance used by agents and reply suggestions.'
        }
        action={
          canManage
            ? <button className="btn primary" onClick={() => setOpen(true)}><Plus size={17} />New article</button>
            : null
        }
      />

      {error && <div className="error-box">{error}</div>}

      <div className="toolbar">
        <div className="searchbox">
          <Search size={17} />
          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search articles..." />
        </div>
      </div>

      {loading ? (
        <Loader />
      ) : items.length === 0 ? (
        <Empty title="No knowledge articles" />
      ) : (
        <div className="kb-grid">
          {items.map((article) => (
            <button key={article.id} className="kb-card" onClick={() => setSelected(article)}>
              <div className="kb-icon"><BookOpen size={20} /></div>
              <div>
                <span>{article.category || 'General'}</span>
                <h3>{article.title}</h3>
                <p>{article.content.slice(0, 170)}{article.content.length > 170 ? '…' : ''}</p>
                <small>Updated {new Date(article.updated_at).toLocaleDateString()}</small>
              </div>
            </button>
          ))}
        </div>
      )}

      <Modal open={open} onClose={() => setOpen(false)} title="Create knowledge article" wide>
        <form className="form-grid" onSubmit={save}>
          <Field label="Title">
            <input required value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
          </Field>
          <Field label="Category">
            <input value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} />
          </Field>
          <Field label="Article content">
            <textarea required rows="12" value={form.content} onChange={(e) => setForm({ ...form, content: e.target.value })} />
          </Field>
          <label className="check">
            <input
              type="checkbox"
              checked={form.is_published}
              onChange={(e) => setForm({ ...form, is_published: e.target.checked })}
            />
            Published and visible in the help center
          </label>
          <div className="form-actions">
            <button type="button" className="btn" onClick={() => setOpen(false)}>Cancel</button>
            <button className="btn primary">Publish article</button>
          </div>
        </form>
      </Modal>

      <Modal open={!!selected} onClose={() => setSelected(null)} title={selected?.title || ''} wide>
        {selected && (
          <article className="article-view">
            <div className="article-meta">
              {selected.category || 'General'} · {selected.is_published ? 'Published' : 'Draft'}
              {!isCustomer && <> · by {selected.created_by || 'Unknown'}</>}
            </div>
            <p>{selected.content}</p>
          </article>
        )}
      </Modal>
    </>
  )
}
