export const AGENTS = [
  { key: 'needs', name: 'Needs Assessment', desc: 'Understands your circumstances' },
  { key: 'research', name: 'Research', desc: 'Searches trusted public sources' },
  { key: 'eligibility', name: 'Eligibility', desc: 'Checks published criteria' },
  { key: 'planning', name: 'Planning', desc: 'Builds your action plan' },
  { key: 'verification', name: 'Verification', desc: 'Cross-checks every step' },
]

export default function AgentPipeline({ status, traces }) {
  return (
    <ol className="pipeline" aria-label="Agent progress">
      {AGENTS.map((a, i) => {
        const s = status[a.key] || 'waiting'
        const t = traces[a.key]
        return (
          <li key={a.key} className={`agent ${s}`}>
            <div className="agent-dot">{s === 'done' ? '✓' : s === 'error' ? '!' : i + 1}</div>
            <div className="agent-body">
              <div className="agent-name">{a.name} <span className="agent-tag">Agent</span></div>
              <div className="agent-desc">{t?.message || (s === 'running' ? 'Working…' : a.desc)}</div>
              {t?.seconds != null && <div className="agent-time">{t.seconds}s</div>}
            </div>
          </li>
        )
      })}
    </ol>
  )
}
