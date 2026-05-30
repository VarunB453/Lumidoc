/**
 * Mock Service Worker — node-side server used by Vitest. Tests can override
 * specific handlers per-suite via `server.use(...)`.
 */
import { setupServer } from 'msw/node'
import { handlers } from './handlers'

export const server = setupServer(...handlers)
