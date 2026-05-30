import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiTarget = env.VITE_DEV_PROXY_TARGET || 'http://localhost:8000'

  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    server: {
      host: '0.0.0.0',
      port: 5173,
      proxy: {
        '/api': {
          target: apiTarget,
          changeOrigin: true,
        },
        '/local-files': {
          target: apiTarget,
          changeOrigin: true,
        },
      },
    },
    build: {
      target: 'es2020',
      sourcemap: false,
      // Split vendor chunks for better caching
      rollupOptions: {
        output: {
          manualChunks: {
            // Core React — cached long-term
            'vendor-react': ['react', 'react-dom', 'react-router-dom'],
            // State & data fetching
            'vendor-data': ['@tanstack/react-query', 'zustand', 'axios'],
            // Heavy animation libs — only loaded when needed (lazy pages)
            'vendor-three': ['three'],
            'vendor-gsap': ['gsap'],
            'vendor-framer': ['framer-motion'],
            // Utilities
            'vendor-utils': ['date-fns', 'clsx', 'tailwind-merge', 'lucide-react'],
          },
        },
      },
      // Enable minification optimizations
      minify: 'terser',
      terserOptions: {
        compress: {
          drop_console: true,
          drop_debugger: true,
        },
      },
    },
  }
})
