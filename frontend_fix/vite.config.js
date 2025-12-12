import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      '/chat': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/roadmap': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/recommend': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/dashboard': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/courses': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/skill': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})