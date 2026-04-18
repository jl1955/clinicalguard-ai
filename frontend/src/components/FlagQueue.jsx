import { useState } from 'react'
import RiskBadge from './RiskBadge'
import { postReview } from '../api/client'
import { formatTime, truncate } from '../lib/utils'

const WarningIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4 text-orange-400 shrink-0">
    <path fillRule="evenodd" d="M9.401 3.003c1.155-2 4.043-2 5.197 0l7.355 12.748c1.154 2-.29 4.5-2.599 4.5H4.645c-2.309 0-3.752-2.5-2.598-4.5L9.4 3.003zM12 8.25a.75.75 0 01.75.75v3.75a.75.75 0 01-1.5 0V9a.75.75 0 01.75-.75zm0 8.25a.75.75 0 100-1.5.75.75 0 000 1.5z" clipRule="evenodd" />
  </svg>
)

const CheckIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-12 h-12 text-zinc-600">
    <path fillRule="evenodd" d="M2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12zm13.36-1.814a.75.75 0 10-1.22-.872l-3.236 4.53L9.53 12.22a.75.75 0 00-1.06 1.06l2.25 2.25a.75.75 0 001.14-.094l3.75-5.25z" clipRule="evenodd" />
  </svg>
)

const SpinnerIcon = () => (
  <svg className="animate-spin w-3 h-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
  </svg>
)

const LLM_CHIP = {
  claude:  'bg-purple-950 text-purple-400 border border-purple-900',
  chatgpt: 'bg-slate-900 text-slate-400 border border-slate-700',
}

function FlagItem({ row, onRefresh }) {
  const [loading, setLoading] = useState(null)

  const handleAction = async (action) => {
    setLoading(action)
    try {
      await postReview(row.id, action)
      onRefresh()
    } catch {
      // silently fail — refresh will show current state
    } finally {
      setLoading(null)
    }
  }

  const entities = row.phi_entities ?? []
  const llmCls = LLM_CHIP[row.llm_target] ?? LLM_CHIP.claude

  return (
    <div className="card-hover p-4 mb-2 animate-fade-in">
      <div className="flex items-center gap-2">
        <WarningIcon />
        <span className="font-mono text-rose-400 text-sm">{row.user_id}</span>
        <span className="text-xs text-zinc-300/50 ml-auto shrink-0">{formatTime(row.timestamp)}</span>
      </div>

      <p className="text-xs font-mono text-zinc-200/80 mt-2 leading-relaxed">
        {truncate(row.prompt, 90)}
      </p>

      {entities.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-2">
          {entities.map((e, i) => (
            <span
              key={i}
              className="bg-red-950 text-red-400 border border-red-900 text-[10px] font-mono px-1.5 py-0.5 rounded"
            >
              {e.type}
            </span>
          ))}
        </div>
      )}

      <div className="flex items-center gap-2 mt-2">
        <RiskBadge risk={row.risk_score} />
        {row.llm_target && (
          <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full ${llmCls}`}>
            {row.llm_target}
          </span>
        )}
      </div>

      <div className="flex gap-2 mt-3">
        <button
          className="btn-approve"
          onClick={() => handleAction('approved_override')}
          disabled={!!loading}
        >
          {loading === 'approved_override' ? <SpinnerIcon /> : '✓'}
          Approve Override
        </button>
        <button
          className="btn-block"
          onClick={() => handleAction('confirmed_block')}
          disabled={!!loading}
        >
          {loading === 'confirmed_block' ? <SpinnerIcon /> : '✗'}
          Confirm Block
        </button>
      </div>
    </div>
  )
}

export default function FlagQueue({ logs, onRefresh }) {
  const flagged = logs.filter(l => l.status === 'flagged')

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-surface-border shrink-0">
        <h2 className="font-display text-lg text-rose-300">Review Queue</h2>
        <div className="flex items-center gap-1.5 ml-auto">
          {flagged.length > 0 && (
            <span className="w-2 h-2 bg-red-400 rounded-full animate-pulse" />
          )}
          <span className={`text-xs font-mono px-2 py-0.5 rounded-full border ${
            flagged.length > 0
              ? 'bg-red-950 text-red-400 border-red-900'
              : 'bg-surface-muted text-zinc-300/40 border-surface-border'
          }`}>
            {flagged.length} pending
          </span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-3">
        {flagged.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full gap-3 py-12">
            <CheckIcon />
            <p className="font-display text-zinc-500 text-lg">All clear</p>
            <p className="text-xs text-zinc-300/40">No queries pending review</p>
          </div>
        ) : (
          flagged.map(row => (
            <FlagItem key={row.id} row={row} onRefresh={onRefresh} />
          ))
        )}
      </div>
    </div>
  )
}
