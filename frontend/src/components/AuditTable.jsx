import { useState, useEffect, useRef, useCallback } from 'react'
import RiskBadge from './RiskBadge'
import StatusBadge from './StatusBadge'
import { getLogs } from '../api/client'
import { formatTime, truncate } from '../lib/utils'

const ShieldIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4 text-red-400">
    <path fillRule="evenodd" d="M11.484 2.17a.75.75 0 011.032 0 11.209 11.209 0 007.877 3.08.75.75 0 01.722.515 12.74 12.74 0 01.635 3.985c0 5.942-4.064 10.933-9.563 12.348a.749.749 0 01-.386 0C6.314 20.683 2.25 15.692 2.25 9.75c0-1.39.223-2.73.635-3.985a.75.75 0 01.722-.516l.143.001c2.996 0 5.718-1.17 7.734-3.08zM12 8.25a.75.75 0 01.75.75v3.75a.75.75 0 01-1.5 0V9a.75.75 0 01.75-.75zM12 15a.75.75 0 000 1.5.75.75 0 000-1.5z" clipRule="evenodd" />
  </svg>
)

const EyeIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
    <path d="M12 15a3 3 0 100-6 3 3 0 000 6z" />
    <path fillRule="evenodd" d="M1.323 11.447C2.811 6.976 7.028 3.75 12.001 3.75c4.97 0 9.185 3.223 10.675 7.69.12.362.12.752 0 1.113-1.487 4.471-5.705 7.697-10.677 7.697-4.97 0-9.186-3.223-10.675-7.69a1.762 1.762 0 010-1.113zM17.25 12a5.25 5.25 0 11-10.5 0 5.25 5.25 0 0110.5 0z" clipRule="evenodd" />
  </svg>
)

const LLM_CHIP = {
  claude:  'bg-purple-950 text-purple-400 border border-purple-900 text-[10px] font-mono px-2 py-0.5 rounded-full',
  chatgpt: 'bg-slate-900 text-slate-400 border border-slate-700 text-[10px] font-mono px-2 py-0.5 rounded-full',
}

const COLS = [
  { label: 'TIME',   cls: 'w-20' },
  { label: 'USER',   cls: 'w-32' },
  { label: 'LLM',    cls: 'w-24' },
  { label: 'PROMPT', cls: '' },
  { label: 'RISK',   cls: 'w-24' },
  { label: 'PHI',    cls: 'w-10 text-center' },
  { label: 'STATUS', cls: 'w-36' },
  { label: '',       cls: 'w-10' },
]

export default function AuditTable({ onSelectRow, onStatsRefresh }) {
  const [rows, setRows] = useState([])
  const [newIds, setNewIds] = useState(new Set())
  const prevIds = useRef(new Set())

  const fetchLogs = useCallback(async () => {
    try {
      const { data } = await getLogs(100)
      const incoming = Array.isArray(data) ? data : (data.logs ?? [])
      const fresh = incoming.filter(r => !prevIds.current.has(r.id))
      if (fresh.length > 0) {
        setNewIds(new Set(fresh.map(r => r.id)))
        prevIds.current = new Set(incoming.map(r => r.id))
        setRows(incoming)
        onStatsRefresh?.()
        setTimeout(() => setNewIds(new Set()), 1200)
      } else {
        setRows(incoming)
      }
    } catch {
      // backend not ready
    }
  }, [onStatsRefresh])

  useEffect(() => {
    fetchLogs()
    const id = setInterval(fetchLogs, 5000)
    return () => clearInterval(id)
  }, [fetchLogs])

  return (
    <div className="w-full overflow-x-auto">
      <table className="w-full">
        <thead className="bg-surface-muted sticky top-0 z-10">
          <tr>
            {COLS.map((col, i) => (
              <th
                key={i}
                className={`text-[10px] font-mono text-zinc-500 uppercase tracking-widest px-4 py-3 text-left ${col.cls}`}
              >
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.length === 0 ? (
            <tr>
              <td colSpan={8} className="text-center text-zinc-600 font-mono text-sm py-16">
                No queries intercepted yet
              </td>
            </tr>
          ) : (
            rows.map(row => (
              <tr
                key={row.id}
                className={`table-row ${newIds.has(row.id) ? 'animate-row-flash' : ''}`}
                onClick={() => onSelectRow?.(row)}
              >
                <td className="px-4 py-3 font-mono text-xs text-zinc-300/60 whitespace-nowrap">
                  {formatTime(row.timestamp)}
                </td>
                <td className="px-4 py-3 font-mono text-xs text-rose-400 truncate max-w-[120px]">
                  {row.user_id}
                </td>
                <td className="px-4 py-3">
                  {row.llm_target ? (
                    <span className={LLM_CHIP[row.llm_target] ?? LLM_CHIP.claude}>
                      {row.llm_target}
                    </span>
                  ) : (
                    <span className="text-zinc-300/20">—</span>
                  )}
                </td>
                <td className="px-4 py-3 font-mono text-xs text-zinc-200/80 max-w-xs">
                  <span title={row.prompt}>{truncate(row.prompt, 55)}</span>
                </td>
                <td className="px-4 py-3">
                  <RiskBadge risk={row.risk_score} />
                </td>
                <td className="px-4 py-3 text-center">
                  {row.phi_detected ? <ShieldIcon /> : <span className="text-zinc-300/20">—</span>}
                </td>
                <td className="px-4 py-3">
                  <StatusBadge status={row.status} />
                </td>
                <td className="px-4 py-3">
                  <button
                    className="text-zinc-500 hover:text-rose-400 transition-colors"
                    onClick={e => { e.stopPropagation(); onSelectRow?.(row) }}
                  >
                    <EyeIcon />
                  </button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}
