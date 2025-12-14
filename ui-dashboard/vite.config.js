import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 7103,
    proxy: {
      '/api': {
        target: 'http://localhost:5103',
        changeOrigin: true,
        secure: false,
      },
    },
  },
})
