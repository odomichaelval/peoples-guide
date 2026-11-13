import { useState } from 'react'
import { api } from '../api.js'
import Logo from '../components/Logo.jsx'

export default function Login({ onLogin }) {
  const [mode, setMode] = useState('login')
  const [form, setForm] = useState({ username: '', password: '', full_name: '' })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value })

  async function submit(e) {
    e.preventDefault()
    setError(''); setBusy(true)
    try {
      const data = mode === 'login'
        ? await api.login(form.username, form.password)
        : await api.register(form.username, form.password, form.full_name)
      onLogin(data)
    } catch (err) {
      setError(err.message || 'Something went wrong')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="login-page">
      <section className="login-hero">
        <div className="brand"><Logo size={44} /><span>People's Guide</span></div>
        <h1>The Right Support.<br />The Right Information.<br /><em>One Place.</em></h1>
        <p>Describe your situation in your own words. Five AI agents find the public services you may be entitled to,
          check the rules, and give you a step-by-step plan with official links.</p>
        <ul className="hero-points">
          <li><b>Private by design</b> - AI runs locally on an NVIDIA DGX Spark. Your story never goes to a cloud AI.</li>
          <li><b>Verified</b> - every recommendation is cross-checked against GOV.UK, Sheffield City Council and NHS sources.</li>
          <li><b>Practical</b> - a prioritised action plan, not a wall of text.</li>
        </ul>
      </section>

      <section className="login-card-wrap">
        <form className="login-card" onSubmit={submit}>
          <h2>{mode === 'login' ? 'Sign in' : 'Create an account'}</h2>
          <p className="muted">{mode === 'login' ? 'Welcome back.' : 'It only takes a moment.'}</p>
          {mode === 'register' && (
            <label>Full name (optional)
              <input value={form.full_name} onChange={set('full_name')} autoComplete="name" />
            </label>
          )}
          <label>Username
            <input value={form.username} onChange={set('username')} required minLength={2} autoComplete="username" autoFocus />
          </label>
          <label>Password
            <input type="password" value={form.password} onChange={set('password')} required minLength={6}
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'} />
          </label>
          {error && <div className="error" role="alert">{error}</div>}
          <button className="btn primary" disabled={busy}>{busy ? 'Please wait…' : mode === 'login' ? 'Sign in' : 'Create account'}</button>
          <button type="button" className="link" onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError('') }}>
            {mode === 'login' ? 'New here? Create an account' : 'Already have an account? Sign in'}
          </button>
        </form>
        <p className="tiny">Prototype for the NVIDIA DGX Spark hackathon. Guidance only - not legal or financial advice.</p>
      </section>
    </div>
  )
}
