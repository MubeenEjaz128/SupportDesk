import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, ArrowRight, Sparkles } from 'lucide-react'
import { api } from '../lib/api'
import { useAuth } from '../context/AuthContext'

const initial = {
  name: '',
  email: '',
  phone: '',
  company: '',
  password: '',
  password_confirm: '',
}

export default function Register() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [form, setForm] = useState(initial)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const change = (key) => (e) => setForm({ ...form, [key]: e.target.value })

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await api('/auth/register/', {
        method: 'POST',
        body: JSON.stringify(form),
      })
      await login(form.email.trim().toLowerCase(), form.password)
      navigate('/')
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <section className="login-hero">
        <div className="hero-content">
          <div className="hero-brand"><Sparkles />SupportDesk</div>
          <h1>One place for every<br />support request.</h1>
          <p>
            Create an account, open a ticket and keep the full conversation and
            status history together until your issue is resolved.
          </p>
        </div>
      </section>

      <section className="login-panel">
        <form className="login-card register-card" onSubmit={submit}>
          <Link className="back-link" to="/login"><ArrowLeft size={16} />Back to sign in</Link>

          <div>
            <span className="eyebrow">CUSTOMER ACCOUNT</span>
            <h2>Create your account</h2>
            <p>This account is only for your own support requests and conversations.</p>
          </div>

          {error && <div className="error-box">{error}</div>}

          <div className="register-grid">
            <label className="field">
              <span>Full name</span>
              <input required value={form.name} onChange={change('name')} />
            </label>
            <label className="field">
              <span>Email</span>
              <input required type="email" value={form.email} onChange={change('email')} />
            </label>
            <label className="field">
              <span>Phone</span>
              <input value={form.phone} onChange={change('phone')} />
            </label>
            <label className="field">
              <span>Company</span>
              <input value={form.company} onChange={change('company')} />
            </label>
            <label className="field">
              <span>Password</span>
              <input
                required
                type="password"
                minLength="8"
                value={form.password}
                onChange={change('password')}
                autoComplete="new-password"
              />
            </label>
            <label className="field">
              <span>Confirm password</span>
              <input
                required
                type="password"
                minLength="8"
                value={form.password_confirm}
                onChange={change('password_confirm')}
                autoComplete="new-password"
              />
            </label>
          </div>

          <button className="btn primary login-btn" disabled={loading}>
            {loading ? 'Creating account...' : <>Create account <ArrowRight size={18} /></>}
          </button>
        </form>
      </section>
    </div>
  )
}
