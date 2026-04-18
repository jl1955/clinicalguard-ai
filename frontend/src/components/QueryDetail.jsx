import { motion, AnimatePresence } from 'framer-motion'
import RiskBadge from './RiskBadge'
import StatusBadge from './StatusBadge'
import { formatTime } from '../lib/utils'

const XMarkIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
    <path fillRule="evenodd" d="M5.47 5.47a.75.75 0 011.06 0L12 10.94l5.47-5.47a.75.75 0 111.06 1.06L13.06 12l5.47 5.47a.75.75 0 11-1.06 1.06L12 13.06l-5.47 5.47a.75.75 0 01-1.06-1.06L10.94 12 5.47 6.53a.75.75 0 010-1.06z" clipRule="evenodd" />
  </svg>
)

function SectionLabel({ children, dot }) {
  return (
    <div className="flex items-center gap-2 mb-2">
      {dot && <span className={`w-1.5 h-1.5 rounded-full ${dot}`} />}
      <span className="text-[10px] font-mono tracking-widest text-zinc-500 uppercase">{children}</span>
    </div>
  )
}

function CodeBlock({ children, maxH = 'max-h-40' }) {
  return (
    <div className={`bg-surface border border-surface-border rounded-lg p-4 font-mono text-sm text-zinc-200 ${maxH} overflow-y-auto leading-relaxed whitespace-pre-wrap break-words`}>
      {children || <span className="text-zinc-300/30 italic">empty</span>}
    </div>
  )
}

function ComplianceBadge({ status }) {
  const map = {
    COMPLIANT:     'text-rose-400 bg-rose-950 border-rose-800',
    NON_COMPLIANT: 'text-red-400 bg-red-950 border-red-800',
    NEEDS_REVIEW:  'text-orange-400 bg-orange-950 border-orange-800',
  }
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-xs font-mono font-semibold border ${map[status] ?? map.NEEDS_REVIEW}`}>
      {status ?? 'UNKNOWN'}
    </span>
  )
}

export default function QueryDetail({ row, onClose }) {
  return (
    <AnimatePresence>
      {row && (
        <>
          <motion.div
            key="overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40"
            onClick={onClose}
          />
          <motion.div
            key="drawer"
            initial={{ x: 480, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 480, opacity: 0 }}
            transition={{ type: 'spring', damping: 28, stiffness: 300 }}
            className="fixed right-0 top-0 bottom-0 w-[480px] bg-surface-card border-l border-surface-border z-50 flex flex-col overflow-hidden"
          >
            {/* Header */}
            <div className="flex items-start justify-between p-5 border-b border-surface-border shrink-0">
              <div>
                <h2 className="font-display text-xl text-rose-300">Query Detail</h2>
                <p className="text-xs font-mono text-zinc-300/50 mt-0.5">
                  {formatTime(row.timestamp)} &middot; {row.user_id}
                </p>
                <div className="flex items-center gap-2 mt-2">
                  <RiskBadge risk={row.risk_score} />
                  <StatusBadge status={row.status} />
                </div>
              </div>
              <button
                onClick={onClose}
                className="text-zinc-300/40 hover:text-zinc-100 transition-colors p-1 mt-0.5"
              >
                <XMarkIcon />
              </button>
            </div>

            {/* Scrollable body */}
            <div className="flex-1 overflow-y-auto p-5 space-y-5">
              {/* Prompt */}
              <div>
                <SectionLabel>Intercepted Prompt</SectionLabel>
                <CodeBlock maxH="max-h-40">{row.prompt}</CodeBlock>
              </div>

              {/* PHI Detection */}
              {row.phi_detected && row.phi_entities?.length > 0 && (
                <div className="bg-red-950/30 border border-red-900/50 rounded-lg p-4">
                  <SectionLabel dot="bg-red-400 animate-pulse">PHI Entities Detected</SectionLabel>
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="text-[10px] font-mono text-red-600 uppercase tracking-widest">
                        <th className="text-left pb-2">Type</th>
                        <th className="text-left pb-2">Value</th>
                        <th className="text-left pb-2">Confidence</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-red-900/30">
                      {row.phi_entities.map((e, i) => (
                        <tr key={i} className="py-1">
                          <td className="py-1.5 pr-3">
                            <span className="badge-high text-[10px]">{e.type}</span>
                          </td>
                          <td className="py-1.5 pr-3 font-mono text-zinc-200/80 truncate max-w-[140px]">
                            {e.value}
                          </td>
                          <td className="py-1.5">
                            <div className="flex items-center gap-2">
                              <div className="flex-1 h-1.5 bg-red-900/50 rounded-full overflow-hidden">
                                <div
                                  className="h-full bg-zinc-400 rounded-full"
                                  style={{ width: `${Math.round((e.confidence ?? 0) * 100)}%` }}
                                />
                              </div>
                              <span className="text-[10px] font-mono text-zinc-300/60 w-8">
                                {Math.round((e.confidence ?? 0) * 100)}%
                              </span>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* Compliance Check */}
              {row.compliance_check && (
                <div>
                  <SectionLabel>GCP Compliance</SectionLabel>
                  <div className="bg-surface border border-surface-border rounded-lg p-4 space-y-2">
                    <ComplianceBadge status={row.compliance_check.status} />
                    {row.compliance_check.summary && (
                      <p className="text-sm text-zinc-300/80 leading-relaxed">
                        {row.compliance_check.summary}
                      </p>
                    )}
                    {row.compliance_check.guideline && (
                      <p className="text-xs font-mono text-rose-500">{row.compliance_check.guideline}</p>
                    )}
                  </div>
                </div>
              )}

              {/* LLM Response */}
              {row.response && row.status !== 'confirmed_block' && (
                <div>
                  <SectionLabel>LLM Response</SectionLabel>
                  <CodeBlock maxH="max-h-32">{row.response}</CodeBlock>
                </div>
              )}

              {/* Block Reason */}
              {(row.status === 'flagged' || row.status === 'confirmed_block') && row.block_reason && (
                <div className="bg-red-950/50 border border-red-900 rounded-lg p-3">
                  <p className="text-red-400 text-sm font-mono">
                    <span className="mr-1">⚠</span>
                    {row.block_reason}
                  </p>
                </div>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
