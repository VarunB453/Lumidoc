import { describe, expect, it } from 'vitest'

import { isEmail, isNonEmpty, isStrongPassword } from '@/lib/utils/validation'

describe('isEmail', () => {
  it('accepts well-formed addresses', () => {
    expect(isEmail('alice@example.com')).toBe(true)
    expect(isEmail('a.b+tag@sub.domain.io')).toBe(true)
  })

  it('rejects malformed addresses', () => {
    expect(isEmail('')).toBe(false)
    expect(isEmail('alice')).toBe(false)
    expect(isEmail('alice@')).toBe(false)
    expect(isEmail('alice@example')).toBe(false)
    expect(isEmail('alice @example.com')).toBe(false)
  })
})

describe('isStrongPassword', () => {
  it('requires at least 8 chars with a letter and a digit', () => {
    expect(isStrongPassword('Password123')).toBe(true)
    expect(isStrongPassword('abc12345')).toBe(true)
  })

  it('rejects weak passwords', () => {
    expect(isStrongPassword('short1')).toBe(false)
    expect(isStrongPassword('allletters')).toBe(false)
    expect(isStrongPassword('12345678')).toBe(false)
  })
})

describe('isNonEmpty', () => {
  it('returns true for non-blank strings', () => {
    expect(isNonEmpty('hello')).toBe(true)
  })

  it('returns false for blank or nullish values', () => {
    expect(isNonEmpty('')).toBe(false)
    expect(isNonEmpty('   ')).toBe(false)
    expect(isNonEmpty(null)).toBe(false)
    expect(isNonEmpty(undefined)).toBe(false)
  })
})
