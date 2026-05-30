import { useEffect, useRef } from 'react'

const CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=[]{}|;:,.<>?/~`'

export default function AsciiBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let animationId: number
    const chars: { x: number; y: number; char: string; opacity: number }[] = []
    const gridSize = 14
    const rows = Math.ceil(window.innerHeight / gridSize)
    const cols = Math.ceil(window.innerWidth / gridSize)

    canvas.width = window.innerWidth
    canvas.height = window.innerHeight

    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        chars.push({
          x: c * gridSize,
          y: r * gridSize,
          char: CHARS[Math.floor(Math.random() * CHARS.length)],
          opacity: 0.01 + Math.random() * 0.04,
        })
      }
    }

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      ctx.font = '11px JetBrains Mono'
      ctx.textBaseline = 'top'

      chars.forEach((c) => {
        const flicker = c.opacity + (Math.random() - 0.5) * 0.02
        const clamped = Math.max(0.005, Math.min(0.05, flicker))
        ctx.fillStyle = `rgba(255,255,255,${clamped})`
        ctx.fillText(c.char, c.x, c.y)
      })

      animationId = requestAnimationFrame(draw)
    }

    draw()

    const handleResize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }
    window.addEventListener('resize', handleResize)

    return () => {
      cancelAnimationFrame(animationId)
      window.removeEventListener('resize', handleResize)
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 z-0 pointer-events-none"
      aria-hidden="true"
    />
  )
}
