import type { Config } from 'tailwindcss'
import forms from '@tailwindcss/forms'

export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#E8622A',
          50: 'rgba(232, 98, 42, 0.08)',
          100: 'rgba(232, 98, 42, 0.12)',
          200: 'rgba(232, 98, 42, 0.2)',
          300: '#F0845A',
          400: '#EC7340',
          500: '#E8622A',
          600: '#D05520',
          700: '#B84A1A',
          800: '#9A3E16',
          900: '#7C3212',
        },
        secondary: {
          DEFAULT: '#4B7BF5',
          50: 'rgba(75, 123, 245, 0.08)',
          100: 'rgba(75, 123, 245, 0.12)',
          200: 'rgba(75, 123, 245, 0.2)',
          300: '#6D94F7',
          400: '#5C87F6',
          500: '#4B7BF5',
          600: '#3A6AE4',
          700: '#2A5AD3',
          800: '#1E4AB2',
          900: '#153A91',
        },
        accent: {
          DEFAULT: '#E8622A',
          50: 'rgba(232, 98, 42, 0.08)',
          100: 'rgba(232, 98, 42, 0.12)',
          200: 'rgba(232, 98, 42, 0.2)',
          300: '#F0845A',
          400: '#EC7340',
          500: '#E8622A',
          600: '#D05520',
          700: '#B84A1A',
          800: '#9A3E16',
          900: '#7C3212',
        },
        surface: {
          DEFAULT: '#0A0A0A',
          soft: 'rgba(10, 10, 10, 0.7)',
          solid: '#111111',
        },
        background: {
          DEFAULT: '#000000',
        },
        text: {
          primary: '#F2F0E8',
          muted: '#9A9A8A',
          light: '#5A5A4E',
        },
      },
      fontFamily: {
        display: ['"Dirtyline 36Daysoftype 2022"', '"Plus Jakarta Sans"', 'sans-serif'],
        heading: ['"Plus Jakarta Sans"', 'sans-serif'],
        body: ['"DM Sans"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
        serif: ['"Instrument Serif"', 'serif'],
        label: ['"DM Mono"', 'monospace'],
        dirtyline: ['"Dirtyline 36Daysoftype 2022"', 'sans-serif'],
      },
      fontSize: {
        xs: ['12px', { lineHeight: '16px' }],
        sm: ['14px', { lineHeight: '20px' }],
        base: ['16px', { lineHeight: '24px' }],
        lg: ['20px', { lineHeight: '28px' }],
        xl: ['24px', { lineHeight: '32px' }],
        '2xl': ['32px', { lineHeight: '40px' }],
        'hero': ['clamp(56px, 9vw, 120px)', { lineHeight: '1.05' }],
      },
      boxShadow: {
        soft: '0 2px 15px -3px rgba(108, 99, 255, 0.1), 0 4px 6px -2px rgba(108, 99, 255, 0.05)',
        'soft-lg':
          '0 10px 40px -10px rgba(108, 99, 255, 0.15), 0 4px 12px -2px rgba(108, 99, 255, 0.08)',
        glow: '0 0 20px rgba(108, 99, 255, 0.3)',
        'glow-accent': '0 0 20px rgba(16, 185, 129, 0.3)',
        'glow-warm': '0 0 30px rgba(232, 98, 42, 0.25)',
        'glow-cool': '0 0 30px rgba(75, 123, 245, 0.25)',
      },
      backdropBlur: {
        xs: '2px',
      },
      animation: {
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-in': 'slideIn 0.3s ease-out',
        'fade-in': 'fadeIn 0.3s ease-out',
        'pulse-soft': 'pulseSoft 2s ease-in-out infinite',
        'bounce-dot': 'bounceDot 1.4s ease-in-out infinite',
        'spin-slow': 'spin 3s linear infinite',
        shimmer: 'shimmer 2s linear infinite',
        'glow-breathe': 'glowBreathe 3s ease-in-out infinite',
        'dash-march': 'dashMarch 1.2s linear infinite',
      },
      keyframes: {
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideIn: {
          '0%': { transform: 'translateX(-20px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        },
        bounceDot: {
          '0%, 80%, 100%': { transform: 'scale(0.6)' },
          '40%': { transform: 'scale(1)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        glowBreathe: {
          '0%, 100%': { opacity: '0.6' },
          '50%': { opacity: '1' },
        },
        dashMarch: {
          'to': { strokeDashoffset: '-20' },
        },
      },
    },
  },
  plugins: [forms],
} satisfies Config
