import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Eye, EyeOff, Check } from 'lucide-react'
import { useStore } from '@/store'
import { cn } from '@/lib/utils'
import { authApi, extractError } from '@/lib/api'
import FuseLogo from '@/components/ui/FuseLogo'
import toast from 'react-hot-toast'

export default function LoginPage() {
  const navigate = useNavigate()
  const { login, signup, isAuthenticated, authReady } = useStore()
  const [isSignUp, setIsSignUp] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    rememberMe: false,
    agreeTerms: false,
  })

  useEffect(() => {
    if (authReady && isAuthenticated) {
      navigate('/dashboard', { replace: true })
    }
  }, [authReady, isAuthenticated, navigate])

  const validateForm = () => {
    const next: Record<string, string> = {}
    if (isSignUp && !formData.name.trim()) next.name = 'Name is required'
    if (!formData.email.trim()) next.email = 'Email is required'
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) next.email = 'Invalid email'
    if (!formData.password) next.password = 'Password is required'
    else if (isSignUp && formData.password.length < 8)
      next.password = 'Password must be at least 8 characters'
    if (isSignUp && !/[a-zA-Z]/.test(formData.password))
      next.password = 'Password must contain letters'
    if (isSignUp && !/\d/.test(formData.password))
      next.password = 'Password must contain digits'
    if (isSignUp && formData.password !== formData.confirmPassword)
      next.confirmPassword = 'Passwords do not match'
    if (isSignUp && !formData.agreeTerms) next.agreeTerms = 'You must agree to the terms'
    setErrors(next)
    return Object.keys(next).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validateForm()) return
    setIsLoading(true)
    try {
      if (isSignUp) {
        await signup(formData.name.trim(), formData.email.trim(), formData.password)
        toast.success('Account created. Welcome!')
      } else {
        await login(formData.email.trim(), formData.password)
        toast.success('Welcome back!')
      }
      navigate('/dashboard', { replace: true })
    } catch (err) {
      toast.error(extractError(err))
    } finally {
      setIsLoading(false)
    }
  }

  const handleGoogleSignIn = () => {
    window.location.href = authApi.googleLoginUrl()
  }

  return (
    <div className="min-h-screen w-full bg-[#0A0A0F] p-3 sm:p-5 lg:p-6 flex items-center justify-center">
      <div className="relative w-full max-w-[1180px] h-[min(94vh,760px)] grid grid-cols-1 lg:grid-cols-2 rounded-2xl overflow-hidden shadow-[0_30px_80px_-20px_rgba(0,0,0,0.6)]">
        {/* Left: aurora art panel */}
        <motion.aside
          initial={{ opacity: 0, scale: 1.02 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.7, ease: 'easeOut' }}
          className="relative hidden lg:flex flex-col justify-between bg-black p-10 overflow-hidden"
        >
          {/* Aurora layers */}
          <div className="absolute inset-0 pointer-events-none">
            <div
              className="absolute -top-1/3 -left-1/4 w-[140%] h-[120%] opacity-90 mix-blend-screen blur-[2px]"
              style={{
                background:
                  'conic-gradient(from 220deg at 30% 40%, rgba(255,32,140,0.95), rgba(255,90,210,0.7), rgba(120,40,220,0.85), rgba(40,80,255,0.9), rgba(0,200,255,0.6), rgba(255,32,140,0.9))',
                filter: 'blur(40px)',
              }}
            />
            <div
              className="absolute inset-0 opacity-80 mix-blend-screen"
              style={{
                background:
                  'radial-gradient(ellipse 80% 60% at 20% 35%, rgba(236,72,153,0.55) 0%, transparent 60%), radial-gradient(ellipse 70% 60% at 60% 70%, rgba(59,130,246,0.55) 0%, transparent 60%), radial-gradient(ellipse 50% 60% at 90% 50%, rgba(168,85,247,0.45) 0%, transparent 60%)',
              }}
            />
            {/* Flowing line strands */}
            <svg
              className="absolute inset-0 w-full h-full opacity-60 mix-blend-screen"
              viewBox="0 0 600 800"
              preserveAspectRatio="none"
            >
              <defs>
                <linearGradient id="strandA" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0%" stopColor="#FF2E9A" stopOpacity="0.0" />
                  <stop offset="50%" stopColor="#FF2E9A" stopOpacity="0.9" />
                  <stop offset="100%" stopColor="#7A3CFF" stopOpacity="0.0" />
                </linearGradient>
                <linearGradient id="strandB" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0%" stopColor="#3B82F6" stopOpacity="0.0" />
                  <stop offset="50%" stopColor="#3B82F6" stopOpacity="0.85" />
                  <stop offset="100%" stopColor="#06B6D4" stopOpacity="0.0" />
                </linearGradient>
              </defs>
              {Array.from({ length: 22 }).map((_, i) => {
                const offset = i * 14
                return (
                  <path
                    key={`a-${i}`}
                    d={`M-50,${120 + offset} C 150,${40 + offset} 380,${260 + offset} 700,${180 + offset}`}
                    fill="none"
                    stroke="url(#strandA)"
                    strokeWidth="1.2"
                    opacity={0.45 + (i % 5) * 0.08}
                  />
                )
              })}
              {Array.from({ length: 22 }).map((_, i) => {
                const offset = i * 14
                return (
                  <path
                    key={`b-${i}`}
                    d={`M-50,${360 + offset} C 180,${280 + offset} 360,${520 + offset} 700,${440 + offset}`}
                    fill="none"
                    stroke="url(#strandB)"
                    strokeWidth="1.2"
                    opacity={0.4 + (i % 5) * 0.08}
                  />
                )
              })}
            </svg>
            {/* subtle vignette */}
            <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-black/70" />
          </div>

          {/* Top eyebrow */}
          <div className="relative flex items-center gap-3 text-white/80">
            <span
              className="text-[11px] tracking-[0.32em] uppercase"
              style={{ fontFamily: '"DM Mono", "JetBrains Mono", monospace' }}
            >
              A Wise Quote
            </span>
            <span className="h-px w-32 bg-white/40" />
          </div>

          {/* Bottom quote */}
          <div className="relative text-white">
            <h2
              className="text-[clamp(48px,6.4vw,84px)] leading-[0.95] tracking-tight"
              style={{ fontFamily: '"Instrument Serif", serif', fontStyle: 'italic' }}
            >
              Get
              <br />
              Everything
              <br />
              You Want
            </h2>
            <p className="mt-5 max-w-sm text-[13px] leading-relaxed text-white/70">
              You can get everything you want if you work hard,
              <br />
              trust the process, and stick to the plan.
            </p>
          </div>
        </motion.aside>

        {/* Right: form panel */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
          className="relative bg-white flex flex-col"
        >
          {/* Brand */}
          <div className="flex items-center justify-center pt-8 pb-6">
            <FuseLogo size="md" variant="dark" />
          </div>

          <div className="flex-1 flex flex-col items-center px-6 sm:px-10">
            <div className="w-full max-w-sm">
              <AnimatePresence mode="wait">
                <motion.div
                  key={isSignUp ? 'signup' : 'login'}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  transition={{ duration: 0.25 }}
                  className="text-center"
                >
                  <h1
                    className="text-[40px] leading-tight text-neutral-900"
                    style={{ fontFamily: '"Instrument Serif", serif' }}
                  >
                    {isSignUp ? 'Create Account' : 'Welcome Back'}
                  </h1>
                  <p className="mt-2 text-[13px] text-neutral-500">
                    {isSignUp
                      ? 'Sign up to get started with your account'
                      : 'Enter your email and password to access your account'}
                  </p>
                </motion.div>
              </AnimatePresence>

              <form onSubmit={handleSubmit} className="mt-7 space-y-4">
                {isSignUp && (
                  <Field
                    label="Full Name"
                    htmlFor="name"
                    error={errors.name}
                  >
                    <input
                      id="name"
                      type="text"
                      placeholder="Enter your name"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      autoComplete="name"
                      className={inputCls(!!errors.name)}
                    />
                  </Field>
                )}

                <Field label="Email" htmlFor="email" error={errors.email}>
                  <input
                    id="email"
                    type="email"
                    placeholder="Enter your email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    autoComplete="email"
                    className={inputCls(!!errors.email)}
                  />
                </Field>

                <Field label="Password" htmlFor="password" error={errors.password}>
                  <div className="relative">
                    <input
                      id="password"
                      type={showPassword ? 'text' : 'password'}
                      placeholder="Enter your password"
                      value={formData.password}
                      onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                      autoComplete={isSignUp ? 'new-password' : 'current-password'}
                      className={cn(inputCls(!!errors.password), 'pr-11')}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword((v) => !v)}
                      aria-label={showPassword ? 'Hide password' : 'Show password'}
                      className="absolute inset-y-0 right-3 my-auto flex h-7 w-7 items-center justify-center rounded-full text-neutral-500 hover:text-neutral-800 hover:bg-neutral-100 transition-colors"
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </Field>

                {isSignUp && (
                  <Field
                    label="Confirm Password"
                    htmlFor="confirm"
                    error={errors.confirmPassword}
                  >
                    <input
                      id="confirm"
                      type="password"
                      placeholder="Re-enter your password"
                      value={formData.confirmPassword}
                      onChange={(e) =>
                        setFormData({ ...formData, confirmPassword: e.target.value })
                      }
                      autoComplete="new-password"
                      className={inputCls(!!errors.confirmPassword)}
                    />
                  </Field>
                )}

                {!isSignUp ? (
                  <div className="flex items-center justify-between pt-1">
                    <label className="flex items-center gap-2 cursor-pointer select-none">
                      <Checkbox
                        checked={formData.rememberMe}
                        onChange={(v) => setFormData({ ...formData, rememberMe: v })}
                      />
                      <span className="text-[13px] text-neutral-700">Remember me</span>
                    </label>
                    <button
                      type="button"
                      className="text-[13px] font-medium text-neutral-900 hover:underline"
                    >
                      Forgot Password
                    </button>
                  </div>
                ) : (
                  <div className="pt-1">
                    <label className="flex items-start gap-2 cursor-pointer select-none">
                      <Checkbox
                        checked={formData.agreeTerms}
                        onChange={(v) => setFormData({ ...formData, agreeTerms: v })}
                      />
                      <span className="text-[13px] text-neutral-700 leading-snug">
                        I agree to the{' '}
                        <a href="#" className="text-neutral-900 underline underline-offset-2">
                          Terms of Service
                        </a>{' '}
                        and{' '}
                        <a href="#" className="text-neutral-900 underline underline-offset-2">
                          Privacy Policy
                        </a>
                      </span>
                    </label>
                    {errors.agreeTerms && (
                      <p className="mt-1.5 text-xs text-red-500">{errors.agreeTerms}</p>
                    )}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={isLoading}
                  className={cn(
                    'mt-2 w-full h-11 rounded-xl bg-neutral-900 text-white text-[14px] font-medium',
                    'hover:bg-black active:scale-[0.99] transition-all',
                    'disabled:opacity-60 disabled:cursor-not-allowed',
                    'shadow-[0_8px_24px_-10px_rgba(0,0,0,0.5)]',
                  )}
                >
                  {isLoading ? (
                    <span className="inline-flex items-center gap-2">
                      <span className="h-4 w-4 rounded-full border-2 border-white/30 border-t-white animate-spin" />
                      Please wait
                    </span>
                  ) : isSignUp ? (
                    'Create Account'
                  ) : (
                    'Sign In'
                  )}
                </button>

                <button
                  type="button"
                  onClick={handleGoogleSignIn}
                  className="w-full h-11 rounded-xl bg-white border border-neutral-200 text-[14px] font-medium text-neutral-800 hover:bg-neutral-50 active:scale-[0.99] transition-all flex items-center justify-center gap-2.5"
                >
                  <GoogleMark />
                  Sign In with Google
                </button>
              </form>
            </div>
          </div>

          <p className="text-center text-[13px] text-neutral-500 pb-8 pt-6">
            {isSignUp ? 'Already have an account?' : "Don't have an account?"}{' '}
            <button
              onClick={() => {
                setIsSignUp(!isSignUp)
                setErrors({})
              }}
              className="font-semibold text-neutral-900 hover:underline"
            >
              {isSignUp ? 'Sign In' : 'Sign Up'}
            </button>
          </p>
        </motion.section>
      </div>
    </div>
  )
}

/* ---------- helpers ---------- */

function inputCls(hasError: boolean) {
  return cn(
    'w-full h-11 rounded-xl px-3.5 text-[14px] text-neutral-900',
    'bg-neutral-100/70 border border-transparent',
    'placeholder:text-neutral-400',
    'transition-colors duration-150',
    'focus:outline-none focus:bg-white focus:border-neutral-300 focus:ring-2 focus:ring-neutral-900/5',
    hasError && 'border-red-300 bg-red-50/50 focus:border-red-400 focus:ring-red-200',
  )
}

function Field({
  label,
  htmlFor,
  error,
  children,
}: {
  label: string
  htmlFor: string
  error?: string
  children: React.ReactNode
}) {
  return (
    <div>
      <label
        htmlFor={htmlFor}
        className="block text-[13px] font-medium text-neutral-800 mb-1.5"
      >
        {label}
      </label>
      {children}
      {error && <p className="mt-1.5 text-xs text-red-500">{error}</p>}
    </div>
  )
}

function Checkbox({
  checked,
  onChange,
}: {
  checked: boolean
  onChange: (v: boolean) => void
}) {
  return (
    <span
      role="checkbox"
      aria-checked={checked}
      tabIndex={0}
      onClick={() => onChange(!checked)}
      onKeyDown={(e) => {
        if (e.key === ' ' || e.key === 'Enter') {
          e.preventDefault()
          onChange(!checked)
        }
      }}
      className={cn(
        'inline-flex h-4 w-4 items-center justify-center rounded-[4px] border transition-colors',
        checked
          ? 'bg-neutral-900 border-neutral-900 text-white'
          : 'bg-white border-neutral-300 hover:border-neutral-500',
      )}
    >
      {checked && <Check className="h-3 w-3" strokeWidth={3} />}
    </span>
  )
}

function GoogleMark() {
  return (
    <svg className="h-4 w-4" viewBox="0 0 24 24" aria-hidden="true">
      <path
        fill="#4285F4"
        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
      />
      <path
        fill="#34A853"
        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
      />
      <path
        fill="#FBBC05"
        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
      />
      <path
        fill="#EA4335"
        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
      />
    </svg>
  )
}
