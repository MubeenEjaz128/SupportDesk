import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Sparkles, ArrowRight, ShieldCheck, Bot, BarChart3 } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ username: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(form.username.trim(), form.password)
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
          <h1>Support that stays<br />clear and organized.</h1>
          <p>
            Customers can raise issues and follow their progress, while support teams
            manage conversations, assignments and responses from one workspace.
          </p>
          <div className="hero-features">
            <div><Bot /><span>AI reply assistance</span></div>
            <div><ShieldCheck /><span>Role-based access</span></div>
            <div><BarChart3 /><span>Support operations dashboard</span></div>
          </div>
        </div>
      </section>

      <section className="login-panel">
        <form className="login-card" onSubmit={submit}>
          <div>
            <span className="eyebrow">WELCOME BACK</span>
            <h2>Sign in to SupportDesk</h2>
            <p>Customers can use their email. Team members can use their username.</p>
          </div>

          {error && <div className="error-box">{error}</div>}

          <label className="field">
            <span>Email or username</span>
            <input
              autoFocus
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              required
              placeholder="you@example.com"
              autoComplete="username"
            />
          </label>

          <label className="field">
            <span>Password</span>
            <input
              type="password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              required
              placeholder="••••••••"
              autoComplete="current-password"
            />
          </label>

          <button className="btn primary login-btn" disabled={loading}>
            {loading ? 'Signing in...' : <>Sign in <ArrowRight size={18} /></>}
          </button>

          <div className="auth-switch">
            <span>Need customer support?</span>
            <Link to="/register">Create a customer account</Link>
          </div>
        </form>
      </section>
    </div>
  )
}
