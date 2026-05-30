import { motion } from 'framer-motion'

export default function TypingIndicator() {
  return (
    <div className="flex items-center gap-1 px-4 py-3 bg-white rounded-2xl shadow-soft rounded-tl-sm w-fit">
      {[0, 1, 2].map((i) => (
        <motion.div
          key={i}
          className="w-2 h-2 rounded-full bg-primary"
          animate={{
            scale: [0.6, 1, 0.6],
            opacity: [0.4, 1, 0.4],
          }}
          transition={{
            duration: 1.4,
            repeat: Infinity,
            delay: i * 0.2,
            ease: 'easeInOut',
          }}
        />
      ))}
    </div>
  )
}
