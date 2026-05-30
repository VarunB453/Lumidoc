import { Navigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useStore } from '@/store'

/**
 * Gate a route behind authentication. While the auth store is hydrating we
 * show a small spinner so users don't see a flash of the login page.
 */
export default function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, authReady } = useStore()
  if (!authReady) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: '#000000' }}>
        <motion.div
          className="w-10 h-10 rounded-full"
          style={{ border: '4px solid rgba(232, 98, 42, 0.2)', borderTopColor: '#E8622A' }}
          animate={{ rotate: 360 }}
          transition={{ duration: 1, ease: 'linear', repeat: Infinity }}
        />
      </div>
    )
  }
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return <>{children}</>
}
