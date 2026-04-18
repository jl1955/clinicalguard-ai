import { useState, useEffect } from 'react'
import { getStats } from '../api/client'

function Skeleton() {
  return (
    <div className="stat-card animate-pulse">
      <div className="h-3 bg-surface-muted rounded w-24 mb-3" />
      <div className="h-8 bg-surface-muted rounded w-16 mb-2" />
      <div className="h-2 bg-surface-muted rounded w-32" />
    </div>
  )
}

const DatabaseIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
    <path d="M21 6.375c0 2.692-4.03 4.875-9 4.875S3 9.067 3 6.375 7.03 1.5 12 1.5s9 2.183 9 4.875z" />
    <path d="M12 12.75c2.685 0 5.19-.586 7.078-1.609a8.283 8.283 0 001.897-1.384c.016.121.025.244.025.368C21 12.817 16.97 15 12 15s-9-2.183-9-4.875c0-.124.009-.247.025-.368a8.285 8.285 0 001.897 1.384C6.809 12.164 9.315 12.75 12 12.75z" />
    <path d="M12 16.5c2.685 0 5.19-.586 7.078-1.609a8.282 8.282 0 001.897-1.384c.016.121.025.244.025.368 0 2.692-4.03 4.875-9 4.875s-9-2.183-9-4.875c0-.124.009-.247.025-.368a8.284 8.284 0 001.897 1.384C6.809 15.914 9.315 16.5 12 16.5z" />
    <path d="M12 20.25c2.685 0 5.19-.586 7.078-1.609a8.282 8.282 0 001.897-1.384c.016.121.025.244.025.368 0 2.692-4.03 4.875-9 4.875s-9-2.183-9-4.875c0-.124.009-.247.025-.368a8.284 8.284 0 001.897 1.384C6.809 19.664 9.315 20.25 12 20.25z" />
  </svg>
)

const ShieldExclamationIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
    <path fillRule="evenodd" d="M11.484 2.17a.75.75 0 011.032 0 11.209 11.209 0 007.877 3.08.75.75 0 01.722.515 12.74 12.74 0 01.635 3.985c0 5.942-4.064 10.933-9.563 12.348a.749.749 0 01-.386 0C6.314 20.683 2.25 15.692 2.25 9.75c0-1.39.223-2.73.635-3.985a.75.75 0 01.722-.516l.143.001c2.996 0 5.718-1.17 7.734-3.08zM12 8.25a.75.75 0 01.75.75v3.75a.75.75 0 01-1.5 0V9a.75.75 0 01.75-.75zM12 15a.75.75 0 000 1.5.75.75 0 000-1.5z" clipRule="evenodd" />
  </svg>
)

const FlagIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
    <path fillRule="evenodd" d="M3 2.25a.75.75 0 01.75.75v.54l1.838-.46a9.75 9.75 0 016.725.738l.108.054a8.25 8.25 0 005.58.652l3.109-.732a.75.75 0 01.917.81 47.784 47.784 0 00.005 10.337.75.75 0 01-.574.812l-3.114.733a9.75 9.75 0 01-6.594-.77l-.108-.054a8.25 8.25 0 00-5.69-.625l-2.202.55V21a.75.75 0 01-1.5 0V3A.75.75 0 013 2.25z" clipRule="evenodd" />
  </svg>
)

const ScaleIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
    <path fillRule="evenodd" d="M12 2.25a.75.75 0 01.75.75v.756a49.106 49.106 0 019.152 1 .75.75 0 01-.152 1.485h-1.918l2.474 10.124a.75.75 0 01-.375.84A6.723 6.723 0 0118 18a6.723 6.723 0 01-3.932-1.245.75.75 0 01-.375-.84l2.474-10.124H12.75v13.28c1.293.076 2.534.343 3.697.776a.75.75 0 01-.262 1.453h-8.37a.75.75 0 01-.262-1.453c1.162-.433 2.404-.7 3.697-.775V6.79H8.208l2.474 10.124a.75.75 0 01-.375.84A6.723 6.723 0 016 18a6.723 6.723 0 01-3.932-1.245.75.75 0 01-.375-.84L4.167 5.791H2.25a.75.75 0 01-.152-1.485 49.105 49.105 0 019.152-1V3a.75.75 0 01.75-.75zm4.878 13.543l1.872-7.662 1.872 7.662h-3.744zm-9.756 0L5.25 8.131l1.872 7.662H7.122z" clipRule="evenodd" />
  </svg>
)

const CARDS = [
  {
    key: 'total_today',
    label: 'Total Queries Today',
    subtitle: 'LLM calls intercepted',
    accent: '#e11d48',
    Icon: DatabaseIcon,
    iconColor: 'text-rose-400',
  },
  {
    key: 'phi_violations',
    label: 'PHI Violations',
    subtitle: 'Protected health info detected',
    accent: '#ef4444',
    Icon: ShieldExclamationIcon,
    iconColor: 'text-red-400',
  },
  {
    key: 'flagged',
    label: 'Flagged for Review',
    subtitle: 'Awaiting human review',
    accent: '#fb923c',
    Icon: FlagIcon,
    iconColor: 'text-orange-400',
  },
  {
    key: 'compliance_failures',
    label: 'Compliance Failures',
    subtitle: 'GCP/21 CFR Part 11 violations',
    accent: '#a78bfa',
    Icon: ScaleIcon,
    iconColor: 'text-purple-400',
  },
]

export default function StatsBar({ onLoad }) {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  const fetchStats = async () => {
    try {
      const { data } = await getStats()
      setStats(data)
      onLoad?.(data)
    } catch {
      // backend may not be ready yet
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStats()
    const id = setInterval(fetchStats, 10000)
    return () => clearInterval(id)
  }, [])

  if (loading) {
    return (
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {CARDS.map((_, i) => <Skeleton key={i} />)}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {CARDS.map(({ key, label, subtitle, accent, Icon, iconColor }) => (
        <div key={key} className="stat-card">
          <div
            className="absolute left-0 top-0 bottom-0 w-1 rounded-l-xl"
            style={{ backgroundColor: accent }}
          />
          <div className="flex items-start justify-between">
            <p className="text-xs font-mono text-zinc-300/60 uppercase tracking-widest leading-tight">
              {label}
            </p>
            <span className={iconColor}>
              <Icon />
            </span>
          </div>
          <p className="text-3xl font-display text-rose-300 mt-1">
            {stats?.[key] ?? 0}
          </p>
          <p className="text-xs text-zinc-300/60 font-body mt-1">{subtitle}</p>
        </div>
      ))}
    </div>
  )
}
