import { Navigate } from 'react-router-dom'
import { useStore } from '@/store'

/**
 * Routes that should redirect authenticated users away (e.g. /login).
 */
export default function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, authReady } = useStore()
  if (authReady && isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }
  return <>{children}</>
}
