import { useEffect } from 'react'
import { useStore } from '@/store'

/**
 * Apply the current preference's theme to <html> by toggling the `.dark` class.
 * Tailwind is configured with darkMode: 'class', so this is enough to swap
 * every dark: variant in the app.
 */
export function useThemeSync() {
  const theme = useStore((s) => s.preferences.theme)

  useEffect(() => {
    const root = document.documentElement
    if (theme === 'dark') {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
  }, [theme])
}
