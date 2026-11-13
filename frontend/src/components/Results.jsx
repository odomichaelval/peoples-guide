const LIKELY = { likely: 'Likely eligible', possible: 'Possibly eligible', unlikely: 'Unlikely' }
const URGENCY = { immediate: 'Urgent', soon: 'Soon', planning: 'Later' }

export function NeedsCard({ needs }) {
  if (!needs) return null
  const c = needs.circumstances || {}
  const facts = Object.entries(c).filter(([, v]) => v !== null && v !== 'unknown' && v !== '')
  return (
    <section className="card">
      <h3>What we understood</h3>
      <p className="lead">{needs.summary}</p>
      <div className="chips">
        {(needs.needs || []).map((n, i) => (
          <span key={i} className={`chip urg-${n.urgency}`} title={n.description}>
            {n.category?.replace(/_/g, ' ')} · {URGENCY[n.urgency] || n.urgency}
          </span>
        ))}
      </div>
      {facts.length > 0 && (
        <dl className="facts">
          {facts.map(([k, v]) => (
            <div key={k}><dt>{k.replace(/_/g, ' ')}</dt><dd>{String(v === true ? 'yes' : v === false ? 'no' : v).replace(/_/g, ' ')}</dd></div>
          ))}
        </dl>
      )}
      {needs.missing_information?.length > 0 && (
        <p className="muted small"><b>Would help to know:</b> {needs.missing_information.join(' · ')}</p>
      )}
    </section>
  )
}

export function PlanCard({ plan, verification }) {
  if (!plan) return null
  return (
    <section className="card plan">
      <div className="plan-head">
        <h3>Your action plan</h3>
        {verification && (
          <span className={`confidence ${verification.confidence >= 0.75 ? 'hi' : verification.confidence >= 0.4 ? 'mid' : 'lo'}`}>
            {verification.verified_steps}/{verification.total_steps} steps verified
          </span>
        )}
      </div>
      {plan.headline && <p className="lead">{plan.headline}</p>}
      <ol className="steps">
        {(plan.steps || []).map((s, i) => (
          <li key={i} className={`step ${s.priority === 0 ? 'crisis' : ''}`}>
            <div className="step-top">
              <span className="step-num">{i + 1}</span>
              <div className="step-title">{s.title}</div>
              <span className={`when when-${s.timeframe?.replace(/\s/g, '')}`}>{s.timeframe}</span>
            </div>
            {s.why && <p><b>Why:</b> {s.why}</p>}
            {s.how && <p><b>How:</b> {s.how}</p>}
            <div className="step-foot">
              {s.url && <a className="btn small" href={s.url} target="_blank" rel="noreferrer">Official page ↗</a>}
              {s.verified !== undefined && (
                <span className={`badge ${s.verified ? 'ok' : 'warn'}`} title={s.verification_note}>
                  {s.verified ? '✓ Verified' : '⚠ Check'} <small>{s.verification_note}</small>
                </span>
              )}
              {(s.sources || []).map((src) => (
                <a key={src.ref} className="ref" href={src.url} target="_blank" rel="noreferrer" title={src.title}>[{src.ref}]</a>
              ))}
            </div>
          </li>
        ))}
      </ol>
      {plan.documents_to_gather?.length > 0 && (
        <div className="sub">
          <h4>Documents to gather</h4>
          <ul className="ticks">{plan.documents_to_gather.map((d, i) => <li key={i}>{d}</li>)}</ul>
        </div>
      )}
      {plan.questions_to_answer?.length > 0 && (
        <div className="sub">
          <h4>Things to check</h4>
          <ul>{plan.questions_to_answer.map((d, i) => <li key={i}>{d}</li>)}</ul>
        </div>
      )}
      {verification?.note && <p className="muted small">🔎 {verification.note}</p>}
    </section>
  )
}

export function ServicesCard({ services }) {
  if (!services?.length) return null
  return (
    <section className="card">
      <h3>Services you may be able to get</h3>
      <div className="services">
        {services.map((s, i) => (
          <article key={i} className={`service ${s.likelihood}`}>
            <div className="service-top">
              <h4>{s.name}</h4>
              <span className={`pill ${s.likelihood}`}>{LIKELY[s.likelihood] || s.likelihood}</span>
            </div>
            <div className="muted small">{s.provider}</div>
            <p>{s.why}</p>
            {s.criteria_met?.length > 0 && <p className="small"><b>✓ You seem to meet:</b> {s.criteria_met.join('; ')}</p>}
            {s.to_confirm?.length > 0 && <p className="small"><b>? To confirm:</b> {s.to_confirm.join('; ')}</p>}
            {s.url && <a href={s.url} target="_blank" rel="noreferrer" className="small">{s.url}</a>}
          </article>
        ))}
      </div>
    </section>
  )
}

export function EvidenceCard({ evidence }) {
  if (!evidence?.length) return null
  return (
    <details className="card evidence">
      <summary><h3>Sources the agents read ({evidence.length})</h3></summary>
      <ul>
        {evidence.map((e) => (
          <li key={e.ref}>
            <b>[{e.ref}]</b> <a href={e.url} target="_blank" rel="noreferrer">{e.title}</a>
            <span className="muted small"> · {e.provider} · relevance {e.score}</span>
          </li>
        ))}
      </ul>
    </details>
  )
}
