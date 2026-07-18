import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // /pico is forwarded by the backend to whichever arm address is live
      // (hotspot 192.168.137.50 or direct-AP 192.168.4.1) — see server.js.
      '/pico': {
        target: 'http://localhost:3000',
        changeOrigin: true
      }
    }
  }
})
