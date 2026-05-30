import { beforeEach, describe, expect, it, vi } from 'vitest'

import { getJwtExpMs, tokenStore } from '@/lib/api/client'
import type { TokenPair } from '@/types'

/** Build a syntactically valid (unsigned) JWT with the given `exp` claim. */
function makeJwt(expSeconds: number): string {
  const b64 = (obj: unknown) =>
    btoa(JSON.stringify(obj)).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
  return `${b64({ alg: 'none' })}.${b64({ exp: expSeconds })}.sig`
}

/** Build a complete TokenPair for tests. */
function pair(access: string, refresh = 'r'): TokenPair {
  return { access_token: access, refresh_token: refresh, token_type: 'bearer', expires_in: 900 }
}

describe('token store', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.restoreAllMocks()
  })

  it('decodes the exp claim from a JWT', () => {
    const token = makeJwt(2_000_000_000)
    expect(getJwtExpMs(token)).toBe(2_000_000_000 * 1000)
  })

  it('returns null for missing or malformed tokens', () => {
    expect(getJwtExpMs(null)).toBeNull()
    expect(getJwtExpMs('not-a-jwt')).toBeNull()
  })

  it('persists and clears token pairs', () => {
    tokenStore.set(pair('a', 'r'))
    expect(tokenStore.getAccess()).toBe('a')
    expect(tokenStore.getRefresh()).toBe('r')

    tokenStore.clear()
    expect(tokenStore.getAccess()).toBeNull()
    expect(tokenStore.getRefresh()).toBeNull()
  })

  it('treats a far-future token as not expired and a past token as expired', () => {
    const future = Math.floor(Date.now() / 1000) + 3600
    tokenStore.set(pair(makeJwt(future)))
    expect(tokenStore.isAccessExpired()).toBe(false)

    const past = Math.floor(Date.now() / 1000) - 3600
    tokenStore.set(pair(makeJwt(past)))
    expect(tokenStore.isAccessExpired()).toBe(true)
  })

  it('notifies subscribers on set and clear', () => {
    const seen: (string | null)[] = []
    const unsubscribe = tokenStore.subscribe((tokens) =>
      seen.push(tokens?.access_token ?? null),
    )

    tokenStore.set(pair('x', 'y'))
    tokenStore.clear()
    unsubscribe()
    tokenStore.set(pair('z', 'w'))

    expect(seen).toEqual(['x', null])
  })
})
