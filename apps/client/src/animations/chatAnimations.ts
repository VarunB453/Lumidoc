import { gsap } from '../lib/gsap-config'

export function animateAIMessage(el: HTMLElement) {
  gsap.fromTo(
    el,
    { y: 16, opacity: 0, filter: 'blur(3px)' },
    { y: 0, opacity: 1, filter: 'blur(0px)', duration: 0.5, ease: 'expo.out' },
  )
}

export function animateUserMessage(el: HTMLElement) {
  gsap.fromTo(
    el,
    { x: 20, opacity: 0, scale: 0.97 },
    { x: 0, opacity: 1, scale: 1, duration: 0.35, ease: 'expo.out' },
  )
}

export function animateTypingIndicator(dotsEl: HTMLElement) {
  return gsap.to(dotsEl.querySelectorAll('.dot'), {
    y: -5, stagger: 0.15, duration: 0.4, ease: 'smooth.in',
    yoyo: true, repeat: -1,
  })
}

export function animateTimestampChip(el: HTMLElement) {
  gsap.fromTo(
    el,
    { scale: 0.85, opacity: 0 },
    { scale: 1, opacity: 1, duration: 0.4, ease: 'elastic.soft' },
  )
}

export function initInputGlowBreathing(wrapperEl: HTMLElement) {
  gsap.to(wrapperEl, {
    '--glow-warm-intensity': '0.30',
    duration: 3, ease: 'sine.inOut', yoyo: true, repeat: -1,
  })
  gsap.to(wrapperEl, {
    '--glow-cool-intensity': '0.32',
    duration: 3.7, ease: 'sine.inOut', yoyo: true, repeat: -1, delay: 0.5,
  })
}

export function onInputFocus(wrapperEl: HTMLElement) {
  gsap.to(wrapperEl, {
    boxShadow:
      '-60px 0 100px -20px rgba(232,98,42,0.38), 60px 0 100px -20px rgba(75,123,245,0.38), 0 0 0 1px rgba(255,255,255,0.1)',
    duration: 0.4, ease: 'smooth.out',
  })
}

export function onInputBlur(wrapperEl: HTMLElement) {
  gsap.to(wrapperEl, {
    boxShadow:
      '-40px 0 80px -20px rgba(232,98,42,0.18), 40px 0 80px -20px rgba(75,123,245,0.18)',
    duration: 0.6, ease: 'smooth.out',
  })
}

export function animateProgressRing(circleEl: SVGElement, percent: number) {
  const circumference = 2 * Math.PI * 20
  gsap.to(circleEl, {
    strokeDashoffset: circumference * (1 - percent / 100),
    duration: 0.6, ease: 'expo.out',
  })
}

export function activateDropzone(borderEl: HTMLElement) {
  gsap.to(borderEl, {
    opacity: 1, scale: 1.01, duration: 0.3, ease: 'smooth.out',
  })
}

export function staggerFileCards(cardEls: HTMLElement[]) {
  gsap.from(cardEls, {
    y: 20, opacity: 0, stagger: 0.06, duration: 0.45, ease: 'expo.out',
  })
}

export function animateSendButton(btnEl: HTMLElement) {
  gsap.timeline()
    .to(btnEl, { scale: 0.88, duration: 0.1, ease: 'smooth.in' })
    .to(btnEl, { scale: 1, duration: 0.4, ease: 'elastic.soft' })
    .to('.send-ripple', { scale: 2.5, opacity: 0, duration: 0.5, ease: 'expo.out' }, '<')
}

export function updatePlayerProgress(fillEl: HTMLElement, percent: number) {
  gsap.to(fillEl, { width: `${percent}%`, duration: 0.2, ease: 'none' })
}
