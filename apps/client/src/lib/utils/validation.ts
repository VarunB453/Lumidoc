/**
 * Lightweight validation helpers used by forms across the app.
 *
 * Add additional validators here rather than re-implementing the same regex in
 * every page.
 */

export function isEmail(value: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)
}

/**
 * Match the backend password rule:
 *  - at least 8 characters
 *  - contains at least one letter and one digit
 */
export function isStrongPassword(value: string): boolean {
  return value.length >= 8 && /[a-zA-Z]/.test(value) && /\d/.test(value)
}

export function isNonEmpty(value: string | null | undefined): value is string {
  return !!value && value.trim().length > 0
}
