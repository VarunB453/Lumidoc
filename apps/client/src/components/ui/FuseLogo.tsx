import { cn } from '@/lib/utils'
import { motion } from 'framer-motion'

interface FuseLogoProps {
  className?: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
  variant?: 'light' | 'dark'
  animate?: boolean
}

const sizes = {
  sm: 'h-6',
  md: 'h-8',
  lg: 'h-10',
  xl: 'h-14',
}

const letters = ['L', 'u', 'm', 'i', 'D', 'o', 'c']

const containerVariants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.08,
      delayChildren: 0.2,
    },
  },
}

const letterVariants = {
  hidden: {
    opacity: 0,
    y: 20,
    rotateX: -90,
    filter: 'blur(8px)',
  },
  visible: {
    opacity: 1,
    y: 0,
    rotateX: 0,
    filter: 'blur(0px)',
    transition: {
      type: 'spring',
      damping: 12,
      stiffness: 100,
      duration: 0.6,
    },
  },
}

const glowVariants = {
  hidden: { opacity: 0, scale: 0.8 },
  visible: {
    opacity: [0, 0.6, 0],
    scale: [0.8, 1.2, 1],
    transition: {
      duration: 2,
      repeat: Infinity,
      repeatType: 'reverse' as const,
      ease: 'easeInOut',
    },
  },
}

/**
 * Animated "LumiDoc" wordmark logo with elegant serif letterforms.
 * Each letter animates in with a staggered spring + blur reveal.
 * Includes a subtle pulsing glow effect behind the text.
 */
export default function FuseLogo({ className, size = 'md', variant = 'light', animate = true }: FuseLogoProps) {
  const color = variant === 'light' ? '#FFFFFF' : '#3B1F0E'
  const glowColor = variant === 'light' ? 'rgba(255,255,255,0.15)' : 'rgba(59,31,14,0.1)'

  if (!animate) {
    return (
      <div
        className={cn(sizes[size], 'flex items-center', className)}
        aria-label="LumiDoc"
      >
        <span
          className="font-bold tracking-wide"
          style={{
            fontFamily: "'Playfair Display', 'Georgia', serif",
            color,
            fontSize: 'inherit',
          }}
        >
          LumiDoc
        </span>
      </div>
    )
  }

  return (
    <motion.div
      className={cn(sizes[size], 'flex items-center relative', className)}
      aria-label="LumiDoc"
      initial="hidden"
      animate="visible"
      variants={containerVariants}
    >
      {/* Subtle glow behind logo */}
      <motion.div
        className="absolute inset-0 rounded-full"
        style={{ background: `radial-gradient(ellipse, ${glowColor}, transparent 70%)` }}
        variants={glowVariants}
        initial="hidden"
        animate="visible"
      />

      {/* Animated letters */}
      <div className="relative flex items-baseline" style={{ perspective: '400px' }}>
        {letters.map((letter, i) => (
          <motion.span
            key={i}
            variants={letterVariants}
            className="inline-block font-bold"
            style={{
              fontFamily: "'Playfair Display', 'Georgia', serif",
              color,
              fontSize: size === 'sm' ? '1.1rem' : size === 'md' ? '1.4rem' : size === 'lg' ? '1.75rem' : '2.25rem',
              transformOrigin: 'bottom center',
            }}
          >
            {letter}
          </motion.span>
        ))}
      </div>
    </motion.div>
  )
}
