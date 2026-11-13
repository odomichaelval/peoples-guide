import { useEffect, useState } from 'react'
import { session } from './api.js'
import Login from './pages/Login.jsx'
import Guide from './pages/Guide.jsx'

export default function App() {
  const [user, setUser] = useState(session.token ? session.user : null)

  useEffect(() => {
    const out = () => setUser(null)
    window.addEventListener('pg-logout', out)
    return () => window.removeEventListener('pg-logout', out)
  }, [])

  if (!user) return <Login onLogin={(data) => { session.save(data); setUser(session.user) }} />
  return <Guide user={user} onLogout={() => { session.clear(); setUser(null) }} />
}
