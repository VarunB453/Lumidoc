export const PAGE_VARIANTS = {
  initial: { opacity: 0, y: 12, filter: 'blur(4px)' },
  animate: {
    opacity: 1, y: 0, filter: 'blur(0px)',
    transition: { duration: 0.45, ease: [0.16, 1, 0.3, 1] as [number, number, number, number] },
  },
  exit: {
    opacity: 0, y: -8, filter: 'blur(2px)',
    transition: { duration: 0.25, ease: [0.7, 0, 0.84, 0] as [number, number, number, number] },
  },
}
