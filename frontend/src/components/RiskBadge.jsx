export default function RiskBadge({ risk }) {
  const config = {
    low:    { label: 'LOW',    cls: 'badge-low',    dot: 'bg-zinc-400' },
    medium: { label: 'MEDIUM', cls: 'badge-medium', dot: 'bg-orange-400' },
    high:   { label: 'HIGH',   cls: 'badge-high',   dot: 'bg-red-400 animate-pulse' },
  }
  const { label, cls, dot } = config[risk] ?? config.low
  return (
    <span className={cls}>
      <span className={`inline-block w-1.5 h-1.5 rounded-full ${dot}`} />
      {label}
    </span>
  )
}
