import { describe, expect, it } from 'vitest'

import { cn, formatDuration, formatFileSize } from '@/lib/utils/format'

describe('formatFileSize', () => {
  it('renders zero bytes', () => {
    expect(formatFileSize(0)).toBe('0 B')
  })

  it('renders bytes under 1 KB', () => {
    expect(formatFileSize(512)).toBe('512 B')
  })

  it('renders kilobytes', () => {
    expect(formatFileSize(1024)).toBe('1 KB')
    expect(formatFileSize(1536)).toBe('1.5 KB')
  })

  it('renders megabytes', () => {
    expect(formatFileSize(1024 * 1024)).toBe('1 MB')
    expect(formatFileSize(1.2 * 1024 * 1024)).toBe('1.2 MB')
  })

  it('renders gigabytes', () => {
    expect(formatFileSize(1024 * 1024 * 1024)).toBe('1 GB')
  })
})

describe('formatDuration', () => {
  it('renders sub-minute durations with zero-padded seconds', () => {
    expect(formatDuration(5)).toBe('0:05')
    expect(formatDuration(59)).toBe('0:59')
  })

  it('renders minutes and seconds', () => {
    expect(formatDuration(83)).toBe('1:23')
    expect(formatDuration(600)).toBe('10:00')
  })

  it('floors fractional seconds', () => {
    expect(formatDuration(83.9)).toBe('1:23')
  })
})

describe('cn', () => {
  it('merges class names', () => {
    expect(cn('a', 'b')).toBe('a b')
  })

  it('drops falsy values', () => {
    expect(cn('a', false, undefined, null, 'b')).toBe('a b')
  })

  it('lets later tailwind classes win on conflict', () => {
    expect(cn('p-2', 'p-4')).toBe('p-4')
  })
})
