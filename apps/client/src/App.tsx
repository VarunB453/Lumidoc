import { useEffect } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import AppRoutes from '@/routes'
import { useStore } from '@/store'
import { useThemeSync } from '@/hooks/useTheme'
import OfflineBanner from '@/components/ui/OfflineBanner'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      refetchOnWindowFocus: false,
      staleTime: 30_000,
    },
  },
})

function App() {
  const hydrate = useStore((s) => s.hydrate)
  useThemeSync()

  useEffect(() => {
    hydrate()
  }, [hydrate])

  useEffect(() => {
    document.documentElement.classList.add('dark')
  }, [])

  return (
    <QueryClientProvider client={queryClient}>
      <OfflineBanner />
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: '#0A0A0A',
            color: '#F2F0E8',
            borderRadius: '12px',
            padding: '12px 16px',
            fontSize: '14px',
            border: '1px solid rgba(255,255,255,0.06)',
          },
          success: { iconTheme: { primary: '#0EC8A0', secondary: '#fff' } },
          error: { iconTheme: { primary: '#E8622A', secondary: '#fff' } },
        }}
      />
      <AppRoutes />
    </QueryClientProvider>
  )
}

export default App
