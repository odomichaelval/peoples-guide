import { useEffect, useRef, useState } from 'react'
import { api } from '../api.js'
import Logo from '../components/Logo.jsx'
import AgentPipeline from '../components/AgentPipeline.jsx'
import { EvidenceCard, NeedsCard, PlanCard, ServicesCard } from '../components/Results.jsx'

const EXAMPLES = [
  "I live in Sheffield and lost my job two weeks ago. I rent privately and I'm worried I can't pay next month's rent or my council tax.",
  "I'm a single mum with two kids in Sheffield, working part-time. Money is really tight and our energy bills are going up.",
  "I'm 68, live alone in a council flat in Sheffield and only have my state pension. Is there any extra help I can get?",
  "I'm a student at Sheffield Hallam and I've run out of money for food this month.",
]

export default function Guide({ user, onLogout }) {
  const [query, setQuery] = useState('')
  const [location, setLocation] = useState('Sheffield')
  const [running, setRunning] = useState(false)
  const [status, setStatus] = useState({})
  const [traces, setTraces] = useState({})
  const [result, setResult] = useState({})
  const [error, setError] = useState('')
  const [health, setHealth] = useState(null)
  const abortRef = useRef(null)

  useEffect(() => { api.health().then(setHealth).catch(() => setHealth({ api: 'down' })) }, [])

  async function run(e) {
    e?.preventDefault()
    if (query.trim().length < 10) { setError('Please tell us a little more about your situation.'); return }
    setError(''); setRunning(true); setStatus({}); setTraces({}); setResult({})
    const ctrl = new AbortController(); abortRef.current = ctrl
    try {
      await api.streamGuide(query, location, (ev, data) => {
        if (ev === 'agent_start') setStatus((s) => ({ ...s, [data.agent]: 'running' }))
        if (ev === 'agent_done') {
          setStatus((s) => ({ ...s, [data.agent]: 'done' }))
          setTraces((t) => ({ ...t, [data.agent]: data.trace }))
          setResult((r) => ({ ...r, ...data.output }))
        }
        if (ev === 'error') {
          setError(data.message)
          setStatus((s) => Object.fromEntries(Object.entries(s).map(([k, v]) => [k, v === 'running' ? 'error' : v])))
        }
      }, ctrl.signal)
    } catch (err) {
      if (err.name !== 'AbortError') setError(err.message)
    } finally {
      setRunning(false)
    }
  }

  function reset() { abortRef.current?.abort(); setQuery(''); setStatus({}); setTraces({}); setResult({}); setError('') }

  const o = health?.ollama
  const started = Object.keys(status).length > 0

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand"><Logo /><span>People's Guide</span></div>
        <div className="topbar-right">
          <span className={`status ${o?.ok && o?.chat_model_ready ? 'ok' : 'bad'}`}
            title={o ? `Models on this Spark: ${(o.models || []).join(', ')}` : ''}>
            <i /> {o?.ok ? (o.chat_model_ready ? `Local AI: ${o.chat_model}` : `Model ${o.chat_model} not pulled`) : 'Local AI offline'}
          </span>
          <span className="who">Hi, {user?.full_name || user?.username}</span>
          <button className="btn ghost small" onClick={onLogout}>Sign out</button>
        </div>
      </header>

      <main className="main">
        <section className="card ask">
          <h2>Tell us what's going on</h2>
          <p className="muted">Write it however you like. The more you share (housing, work, family, health, money), the better the advice.
            <b> Nothing you type is saved or sent to a cloud AI.</b></p>
          <form onSubmit={run}>
            <textarea value={query} onChange={(e) => setQuery(e.target.value)} rows={5} maxLength={4000}
              placeholder="e.g. I've just lost my job and I'm struggling to pay rent…" disabled={running} />
            <div className="ask-row">
              <label className="inline">Area
                <select value={location} onChange={(e) => setLocation(e.target.value)} disabled={running}>
                  <option>Sheffield</option>
                  <option value="England">Elsewhere in England</option>
                </select>
              </label>
              <div className="spacer" />
              {started && !running && <button type="button" className="btn ghost" onClick={reset}>Start again</button>}
              <button className="btn primary" disabled={running}>{running ? 'Agents working…' : 'Find my support →'}</button>
            </div>
          </form>
          {!started && (
            <div className="examples">
              <span className="muted small">Try an example:</span>
              {EXAMPLES.map((ex, i) => <button key={i} className="example" onClick={() => setQuery(ex)}>{ex}</button>)}
            </div>
          )}
          {error && <div className="error" role="alert">{error}</div>}
        </section>

        {started && (
          <div className="results-grid">
            <aside className="side">
              <section className="card">
                <h3>Agents at work</h3>
                <AgentPipeline status={status} traces={traces} />
                <p className="tiny">Running on NVIDIA DGX Spark · orchestrated with LangGraph</p>
              </section>
              {result.plan && <button className="btn ghost full" onClick={() => window.print()}>🖨 Print / save my plan</button>}
            </aside>
            <div className="results">
              <NeedsCard needs={result.needs} />
              <PlanCard plan={result.plan} verification={result.verification} />
              <ServicesCard services={result.eligibility} />
              <EvidenceCard evidence={result.evidence} />
              {result.plan && (
                <p className="disclaimer">People's Guide gives guidance based on published information. It is not legal or financial advice and
                  cannot guarantee eligibility - the organisation running each service makes the final decision.
                  For free one-to-one advice, contact Citizens Advice Sheffield.</p>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
