import { lazy, Suspense } from 'react'
import Sidebar from '@/components/layout/Sidebar'
import { cn } from '@/lib/utils'
import { useStore } from '@/store'
import { useLiteMode } from '@/hooks/useLiteMode'

// Lazy-load heavy WebGL cursor — only downloaded when actually needed
const GhostCursor = lazy(() => import('@/components/ui/GhostCursor'))
const AnimatedCursorWrapper = lazy(() => import('@/components/layout/MainLayout/AnimatedCursorWrapper'))

interface MainLayoutProps {
  children: React.ReactNode
  className?: string
  hideGhostCursor?: boolean
}

export default function MainLayout({ children, className, hideGhostCursor }: MainLayoutProps) {
  const { sidebarCollapsed } = useStore()
  const liteMode = useLiteMode()

  // Skip all heavy visual effects in lite mode
  const showEffects = !liteMode && !hideGhostCursor

  return (
    <div className="relative min-h-screen" style={{ backgroundColor: '#000000' }}>
      {/* Ghost cursor effect — lazy loaded, skipped on slow connections */}
      {showEffects && (
        <Suspense fallback={null}>
          <GhostCursor
            trailLength={50}
            inertia={0.5}
            grainIntensity={0.03}
            bloomStrength={0}
            bloomRadius={0}
            bloomThreshold={1}
            brightness={2}
            color="#B497CF"
            edgeIntensity={0}
          />
        </Suspense>
      )}

      {/* Animated cursor overlay — lazy loaded, skipped on slow connections */}
      {showEffects && (
        <Suspense fallback={null}>
          <AnimatedCursorWrapper />
        </Suspense>
      )}

      <Sidebar />
      <main
        className={cn(
          'relative z-10 min-h-screen transition-[margin-left] duration-300 ease-in-out',
          className,
        )}
        style={{ marginLeft: sidebarCollapsed ? 60 : 240 }}
      >
        {children}
      </main>
    </div>
  )
}
