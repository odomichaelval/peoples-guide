// sessionStorage: the login is forgotten when the browser tab closes (privacy-first).
const TOKEN_KEY = 'pg_token'
const USER_KEY = 'pg_user'

export const session = {
  get token() { return sessionStorage.getItem(TOKEN_KEY) },
  get user() { try { return JSON.parse(sessionStorage.getItem(USER_KEY)) } catch { return null } },
  save(data) {
    sessionStorage.setItem(TOKEN_KEY, data.access_token)
    sessionStorage.setItem(USER_KEY, JSON.stringify({ username: data.username, full_name: data.full_name }))
  },
  clear() { sessionStorage.removeItem(TOKEN_KEY); sessionStorage.removeItem(USER_KEY) },
}

async function request(path, opts = {}) {
  const headers = { 'Content-Type': 'application/json', ...(opts.headers || {}) }
  if (session.token) headers.Authorization = `Bearer ${session.token}`
  const res = await fetch(path, { ...opts, headers })
  if (res.status === 401) { session.clear(); window.dispatchEvent(new Event('pg-logout')) }
  if (!res.ok) {
    let msg = res.statusText
    try { const j = await res.json(); msg = typeof j.detail === 'string' ? j.detail : JSON.stringify(j.detail) } catch {}
    throw new Error(msg)
  }
  return res
}

export const api = {
  login: async (username, password) => (await request('/api/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) })).json(),
  register: async (username, password, full_name) => (await request('/api/auth/register', { method: 'POST', body: JSON.stringify({ username, password, full_name }) })).json(),
  health: async () => (await fetch('/api/health')).json(),
  sources: async () => (await request('/api/sources')).json(),

  // Streams Server-Sent Events from the multi-agent pipeline.
  async streamGuide(query, location, onEvent, signal) {
    const res = await request('/api/guide/stream', { method: 'POST', body: JSON.stringify({ query, location }), signal })
    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let buf = ''
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buf += decoder.decode(value, { stream: true })
      let idx
      while ((idx = buf.indexOf('\n\n')) !== -1) {
        const raw = buf.slice(0, idx); buf = buf.slice(idx + 2)
        const ev = /^event: (.*)$/m.exec(raw)?.[1]
        const data = /^data: (.*)$/m.exec(raw)?.[1]
        if (ev && data) onEvent(ev, JSON.parse(data))
      }
    }
  },
}
