/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // crimson = Tailwind built-in rose (identical hex values) — no custom definition needed
        // silver  = Tailwind built-in zinc  (identical hex values) — no custom definition needed
        // Dark grey surfaces
        surface: {
          DEFAULT: '#0f0f13',
          card:    '#16161d',
          border:  '#27272f',
          muted:   '#1c1c24',
        },
        // Status risk colors (unchanged — semantically fixed)
        risk: {
          low:    '#a1a1aa',
          medium: '#fb923c',
          high:   '#f87171',
        },
      },
      fontFamily: {
        display: ['"DM Serif Display"', 'serif'],
        mono:    ['"JetBrains Mono"', 'monospace'],
        body:    ['"DM Sans"', 'sans-serif'],
      },
      boxShadow: {
        'glow-rose':    '0 0 20px rgba(244, 63, 94, 0.35)',
        'glow-red':     '0 0 16px rgba(248, 113, 113, 0.3)',
        'glow-orange':  '0 0 16px rgba(251, 146, 60, 0.3)',
        'card':         '0 1px 3px rgba(0,0,0,0.5), 0 1px 2px rgba(0,0,0,0.4)',
        'card-hover':   '0 4px 16px rgba(0,0,0,0.6), 0 2px 6px rgba(0,0,0,0.5)',
      },
      animation: {
        'pulse-slow':  'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in':     'fadeIn 0.4s ease-out',
        'slide-in':    'slideIn 0.3s ease-out',
        'glow-pulse':  'glowPulse 2s ease-in-out infinite',
        'row-flash':   'rowFlash 1s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%':   { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideIn: {
          '0%':   { opacity: '0', transform: 'translateX(16px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        glowPulse: {
          '0%, 100%': { boxShadow: '0 0 8px rgba(244, 63, 94, 0.4)' },
          '50%':      { boxShadow: '0 0 20px rgba(244, 63, 94, 0.9)' },
        },
        rowFlash: {
          '0%':   { backgroundColor: 'rgba(248,113,113,0.2)' },
          '100%': { backgroundColor: 'transparent' },
        },
      },
    },
  },
  plugins: [],
}
