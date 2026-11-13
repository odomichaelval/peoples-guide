import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// In dev, /api calls are proxied to FastAPI on :8000
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: { '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true } },
  },
})
