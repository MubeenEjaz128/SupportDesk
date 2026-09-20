import React, { useEffect, useState } from 'react'
import { Save, UserRound } from 'lucide-react'
import { api } from '../lib/api'
import { Field, Loader, PageHeader } from '../components/UI'
import { useAuth } from '../context/AuthContext'

export default function Profile() {
  const { refreshMe } = useAuth()
  const [form, setForm] = useState(null)
  const [error, setError] = useState('')
  const [saved, setSaved] = useState(false)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    api('/auth/profile/')
      .then(setForm)
      .catch((e) => setError(e.message))
  }, [])

  const save = async (e) => {
    e.preventDefault()
    setSaving(true)
    setSaved(false)
    setError('')
    try {
      const data = await api('/auth/profile/', {
        method: 'PATCH',
        body: JSON.stringify({
          name: form.name,
          phone: form.phone,
          company: form.company,
        }),
      })
      setForm(data)
      await refreshMe()
      setSaved(true)
    } catch (e) {
      setError(e.message)
    } finally {
      setSaving(false)
    }
  }

  if (!form && !error) return <Loader label="Loading your profile..." />

  return (
    <>
      <PageHeader
        title="My Profile"
        subtitle="Contact details connected to your customer support account."
      />

      {error && <div className="error-box">{error}</div>}
      {saved && <div className="success-box">Profile updated successfully.</div>}

      {form && (
        <section className="panel profile-panel">
          <div className="profile-heading">
            <div className="avatar profile-avatar"><UserRound size={26} /></div>
            <div>
              <h2>{form.name}</h2>
              <p>{form.email}</p>
            </div>
          </div>

          <form className="form-grid profile-form" onSubmit={save}>
            <Field label="Full name">
              <input
                required
                value={form.name || ''}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
              />
            </Field>
            <Field label="Email">
              <input value={form.email || ''} disabled />
            </Field>
            <Field label="Phone">
              <input
                value={form.phone || ''}
                onChange={(e) => setForm({ ...form, phone: e.target.value })}
              />
            </Field>
            <Field label="Company">
              <input
                value={form.company || ''}
                onChange={(e) => setForm({ ...form, company: e.target.value })}
              />
            </Field>
            <div className="form-actions">
              <button className="btn primary" disabled={saving}>
                <Save size={16} />{saving ? 'Saving...' : 'Save changes'}
              </button>
            </div>
          </form>
        </section>
      )}
    </>
  )
}
