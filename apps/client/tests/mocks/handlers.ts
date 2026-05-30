/**
 * MSW request handlers used during unit and integration tests. Add new
 * handlers next to the feature they describe. Keep the default to a smoke set
 * that lets the app boot.
 */
import { http, HttpResponse } from 'msw'

const API_BASE = '/api/v1'

export const handlers = [
  http.get(`${API_BASE}/users/me`, () =>
    HttpResponse.json(
      {
        id: 'test-user',
        email: 'test@example.com',
        name: 'Test User',
        avatar_url: null,
      },
      { status: 200 },
    ),
  ),
  http.get(`${API_BASE}/files`, () => HttpResponse.json({ items: [] })),
  http.get(`${API_BASE}/chat/conversations`, () => HttpResponse.json([])),
]
