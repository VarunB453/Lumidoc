/**
 * Public surface for the API client. Importing from `@/lib/api` continues to
 * work after the split into `client.ts` / `interceptors.ts` / `endpoints.ts`.
 *
 * Importing this barrel registers the request/response interceptors as a
 * side-effect of evaluating `./interceptors`.
 */
import api from './client'
import './interceptors'

export {
  API_BASE_URL,
  API_ORIGIN,
  REQUEST_TIMEOUT_MS,
  api,
  tokenStore,
} from './client'

export { buildAssetUrl, extractError, refreshTokens } from './interceptors'

export {
  authApi,
  userApi,
  filesApi,
  chatApi,
  summariesApi,
  timestampsApi,
  miscApi,
  type StreamHandle,
  type StreamHandlers,
} from './endpoints'

export default api
