import { gsap } from '../lib/gsap-config'

export function collapseSidebar(sidebarEl: HTMLElement, iconRailEl: HTMLElement) {
  const tl = gsap.timeline()
  tl.to(sidebarEl, { width: 0, opacity: 0, duration: 0.4, ease: 'expo.out' })
    .to(iconRailEl, { x: -8, opacity: 0.6, duration: 0.3 }, '<')
  return tl
}

export function expandSidebar(sidebarEl: HTMLElement, iconRailEl: HTMLElement) {
  const tl = gsap.timeline()
  tl.to(sidebarEl, { width: 280, opacity: 1, duration: 0.45, ease: 'expo.out' })
    .to(iconRailEl, { x: 0, opacity: 1, duration: 0.3 }, '<+0.1')
  return tl
}

export function staggerHistoryItems(itemEls: HTMLElement[]) {
  gsap.from(itemEls, {
    x: -16, opacity: 0, stagger: 0.04, duration: 0.35, ease: 'expo.out', delay: 0.15,
  })
}
