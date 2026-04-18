import { useState, useEffect, useCallback } from 'react'
import { AnimatePresence } from 'framer-motion'
import { getLogs } from './api/client'
import StatsBar from './components/StatsBar'
import AuditTable from './components/AuditTable'
import FlagQueue from './components/FlagQueue'
import QueryDetail from './components/QueryDetail'

const ShieldIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" className="w-8 h-8">
    <defs>
      <linearGradient id="shieldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#f43f5e" />
        <stop offset="100%" stopColor="#be123c" />
      </linearGradient>
    </defs>
    <path
      fillRule="evenodd"
      clipRule="evenodd"
      d="M11.484 2.17a.75.75 0 011.032 0 11.209 11.209 0 007.877 3.08.75.75 0 01.722.515 12.74 12.74 0 01.635 3.985c0 5.942-4.064 10.933-9.563 12.348a.749.749 0 01-.386 0C6.314 20.683 2.25 15.692 2.25 9.75c0-1.39.223-2.73.635-3.985a.75.75 0 01.722-.516l.143.001c2.996 0 5.718-1.17 7.734-3.08z"
      fill="url(#shieldGrad)"
    />
  </svg>
)

function Clock() {
  const [time, setTime] = useState('')
  useEffect(() => {
    const tick = () => setTime(new Date().toLocaleTimeString('en-US', { hour12: false }))
    tick()
    const id = setInterval(tick, 1000)
    return () => clearInterval(id)
  }, [])
  return <span className="text-xs font-mono text-zinc-300/50">{time}</span>
}

export default function App() {
  const [logs, setLogs] = useState([])
  const [selectedRow, setSelectedRow] = useState(null)

  const refreshLogs = useCallback(async () => {
    try {
      const { data } = await getLogs(100)
      const incoming = Array.isArray(data) ? data : (data.logs ?? [])
      setLogs(incoming)
    } catch {
      // backend may not be ready
    }
  }, [])

  useEffect(() => {
    refreshLogs()
    const id = setInterval(refreshLogs, 5000)
    return () => clearInterval(id)
  }, [refreshLogs])

  const flaggedLogs = logs.filter(l => l.status === 'flagged')

  return (
    <div className="flex flex-col h-screen overflow-hidden">
      {/* Header */}
      <header className="sticky top-0 z-50 h-16 px-6 flex items-center justify-between bg-surface-card/90 backdrop-blur-sm border-b border-surface-border shrink-0">
        <div className="flex items-center gap-3">
          <ShieldIcon />
          <span className="font-display text-xl text-zinc-100">ClinicalGuard</span>
          <span className="font-display text-xl text-rose-400">AI</span>
          <span className="text-surface-border mx-1">·</span>
          <span className="text-xs font-mono text-zinc-300/50 hidden sm:inline">
            Clinical Trial LLM Governance
          </span>
        </div>
        <div className="flex items-center gap-3">
          <span className="w-2 h-2 bg-rose-500 rounded-full animate-glow-pulse" />
          <span className="text-xs font-mono text-rose-400 tracking-widest hidden sm:inline">
            MONITORING ACTIVE
          </span>
          <span className="text-surface-border hidden sm:inline">|</span>
          <Clock />
        </div>
      </header>

      {/* Main */}
      <main className="flex-1 overflow-hidden p-6 flex flex-col gap-4 min-h-0">
        {/* Stats */}
        <StatsBar />

        {/* Two-column layout */}
        <div className="flex-1 flex gap-4 overflow-hidden min-h-0">
          {/* Audit Log */}
          <div className="card flex-1 min-w-0 flex flex-col overflow-hidden">
            <div className="flex items-center gap-3 px-4 py-3 border-b border-surface-border shrink-0">
              <h2 className="font-display text-rose-300">Audit Log</h2>
              <span className="text-xs font-mono bg-surface-muted text-zinc-300/50 border border-surface-border px-2 py-0.5 rounded-full">
                {logs.length} entries
              </span>
            </div>
            <div className="flex-1 overflow-y-auto">
              <AuditTable onSelectRow={setSelectedRow} onStatsRefresh={refreshLogs} />
            </div>
          </div>

          {/* Flag Queue */}
          <div className="card w-80 shrink-0 overflow-hidden flex flex-col">
            <FlagQueue logs={flaggedLogs} onRefresh={refreshLogs} />
          </div>
        </div>
      </main>

      {/* Query Detail Drawer */}
      <AnimatePresence>
        {selectedRow && (
          <QueryDetail row={selectedRow} onClose={() => setSelectedRow(null)} />
        )}
      </AnimatePresence>
    </div>
  )
}
