/**
 * Vitest global setup.
 *
 * - Registers @testing-library/jest-dom matchers (toBeInTheDocument, etc.).
 * - Cleans up the DOM after every test to keep tests isolated.
 * - Stubs browser APIs that jsdom does not implement but components rely on.
 */
import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach, vi } from 'vitest'

afterEach(() => {
  cleanup()
})

// jsdom does not implement matchMedia; several UI hooks (theme, online status)
// read it on mount.
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  }),
})

// jsdom lacks IntersectionObserver, used by lazy-loading panels.
class MockIntersectionObserver {
  observe = vi.fn()
  unobserve = vi.fn()
  disconnect = vi.fn()
  takeRecords = vi.fn(() => [])
  root = null
  rootMargin = ''
  thresholds = []
}
Object.defineProperty(window, 'IntersectionObserver', {
  writable: true,
  value: MockIntersectionObserver,
})
