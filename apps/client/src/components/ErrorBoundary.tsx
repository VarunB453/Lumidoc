import React from 'react'
import { AlertTriangle, RefreshCw } from 'lucide-react'
import Button from '@/components/ui/Button'

type Props = {
  children: React.ReactNode
}

type State = {
  hasError: boolean
}

export default class ErrorBoundary extends React.Component<Props, State> {
  state: State = { hasError: false }

  static getDerivedStateFromError(): State {
    return { hasError: true }
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error('route_render_failed', error, info)
  }

  render() {
    if (!this.state.hasError) {
      return this.props.children
    }

    return (
      <main className="min-h-screen bg-background gradient-mesh px-6 py-10">
        <div className="mx-auto flex min-h-[70vh] max-w-lg flex-col items-center justify-center text-center">
          <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-full bg-red-100 text-red-600 dark:bg-red-500/15 dark:text-red-300">
            <AlertTriangle className="h-6 w-6" aria-hidden="true" />
          </div>
          <h1 className="text-2xl font-semibold text-text-primary">Something went wrong</h1>
          <p className="mt-3 text-sm leading-6 text-text-muted">
            This view could not render. Refresh the page to restore the application state.
          </p>
          <Button className="mt-6" onClick={() => window.location.reload()}>
            <RefreshCw className="mr-2 h-4 w-4" aria-hidden="true" />
            Refresh
          </Button>
        </div>
      </main>
    )
  }
}
