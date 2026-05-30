/**
 * Thin analytics façade. Today this is a no-op that logs in development so we
 * can swap in a real provider (PostHog, Segment, GA4, …) without touching
 * call sites.
 */
type EventProps = Record<string, unknown>

const isDev = import.meta.env.DEV

export const analytics = {
  track(event: string, props: EventProps = {}) {
    if (isDev) {
      console.debug('[analytics]', event, props)
    }
  },
  identify(userId: string, traits: EventProps = {}) {
    if (isDev) {
      console.debug('[analytics] identify', userId, traits)
    }
  },
  page(name: string, props: EventProps = {}) {
    if (isDev) {
      console.debug('[analytics] page', name, props)
    }
  },
}
