import { cn } from '@/lib/utils'

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  glass?: boolean
  hover?: boolean
}

export default function Card({ className, glass = false, hover = false, children, ...props }: CardProps) {
  return (
    <div
      className={cn(
        'rounded-2xl transition-all duration-200',
        glass ? 'glass' : '',
        hover && 'hover:-translate-y-0.5 hover:shadow-soft-lg cursor-pointer',
        className
      )}
      style={{
        backgroundColor: '#0A0A0A',
        border: '1px solid rgba(255, 255, 255, 0.06)',
      }}
      {...props}
    >
      {children}
    </div>
  )
}
