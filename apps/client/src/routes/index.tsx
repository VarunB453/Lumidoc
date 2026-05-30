import { useEffect, lazy, Suspense } from 'react'
import { Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import ErrorBoundary from '@/components/ErrorBoundary'
import { useStore } from '@/store'
import { tokenStore } from '@/lib/api'
import PrivateRoute from './PrivateRoute'

// Lazy-load all pages for code splitting — each page becomes its own chunk
const LoginPage = lazy(() => import('@/pages/LoginPage'))
const DashboardPage = lazy(() => import('@/pages/DashboardPage'))
const ChatPage = lazy(() => import('@/pages/ChatPage'))
const UploadPage = lazy(() => import('@/pages/UploadPage'))
const FilesPage = lazy(() => import('@/pages/FilesPage'))
const SettingsPage = lazy(() => import('@/pages/SettingsPage'))

function PageLoader() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
    </div>
  )
}

/**
 * The Google OAuth flow redirects to `/auth/callback#access_token=...&refresh_token=...`.
 * We pull the tokens from the URL fragment, store them, then rehydrate.
 */
function OAuthCallback() {
  const navigate = useNavigate()
  const hydrate = useStore((s) => s.hydrate)

  useEffect(() => {
    const fragment = window.location.hash.slice(1)
    const params = new URLSearchParams(fragment)
    const access_token = params.get('access_token')
    const refresh_token = params.get('refresh_token')
    const expires_in = Number(params.get('expires_in') || '0')
    if (access_token && refresh_token) {
      tokenStore.set({
        access_token,
        refresh_token,
        token_type: 'bearer',
        expires_in,
      })
      hydrate().finally(() => navigate('/dashboard', { replace: true }))
    } else {
      navigate('/login', { replace: true })
    }
  }, [hydrate, navigate])

  return (
    <div className="min-h-screen flex items-center justify-center bg-background gradient-mesh">
      <p className="text-text-muted">Signing you in…</p>
    </div>
  )
}

export default function AppRoutes() {
  const location = useLocation()
  return (
    <ErrorBoundary key={location.pathname}>
      <Suspense fallback={<PageLoader />}>
        <Routes location={location} key={location.pathname}>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/landing" element={<Navigate to="/dashboard" replace />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/auth/callback" element={<OAuthCallback />} />
          <Route
            path="/dashboard"
            element={
              <PrivateRoute>
                <DashboardPage />
              </PrivateRoute>
            }
          />
          <Route
            path="/chat/:id"
            element={
              <PrivateRoute>
                <ChatPage />
              </PrivateRoute>
            }
          />
          <Route
            path="/upload"
            element={
              <PrivateRoute>
                <UploadPage />
              </PrivateRoute>
            }
          />
          <Route
            path="/files"
            element={
              <PrivateRoute>
                <FilesPage />
              </PrivateRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <PrivateRoute>
                <SettingsPage />
              </PrivateRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Suspense>
    </ErrorBoundary>
  )
}
