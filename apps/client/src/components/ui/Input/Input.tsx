import { forwardRef } from 'react'
import { cn } from '@/lib/utils'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  helperText?: string
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, helperText, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-text-primary mb-1.5">
            {label}
          </label>
        )}
        <input
          ref={ref}
          className={cn(
            'w-full rounded-xl border-2 px-4 py-3 text-sm transition-all duration-200',
            'bg-white/80 backdrop-blur-sm',
            'placeholder:text-text-light',
            'focus-ring focus:border-primary/50',
            error
              ? 'border-red-400 focus:border-red-400 focus:ring-red-400/30'
              : 'border-primary-100 hover:border-primary-200 focus:border-primary',
            className
          )}
          {...props}
        />
        {error && (
          <p className="mt-1.5 text-xs text-red-500 font-medium">{error}</p>
        )}
        {helperText && !error && (
          <p className="mt-1.5 text-xs text-text-muted">{helperText}</p>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'

export default Input
