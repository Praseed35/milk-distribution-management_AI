import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: process.env.VITE_API_PROXY_TARGET || 'http://localhost:8000',
        // Keep the browser's Host header so FastAPI trailing-slash redirects
        // (307) point back at the frontend origin instead of the proxied
        // backend origin, which would bypass the proxy and get CORS-blocked.
        changeOrigin: false,
      },
    },
  },
})
