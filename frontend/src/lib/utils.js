import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs) {
  return twMerge(clsx(inputs))
}

export function formatTime(isoString) {
  if (!isoString) return '--'
  return new Date(isoString).toLocaleTimeString('en-US', {
    hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false
  })
}

export function truncate(str, n = 60) {
  if (!str) return ''
  return str.length > n ? str.slice(0, n) + '\u2026' : str
}
