const STATUS_MAP = {
  clean:             { cls: 'badge-clean',    label: 'CLEAN' },
  flagged:           { cls: 'badge-flagged',  label: 'FLAGGED' },
  approved_override: { cls: 'badge-approved', label: 'APPROVED' },
  confirmed_block:   { cls: 'badge-blocked',  label: 'BLOCKED' },
}

export default function StatusBadge({ status }) {
  const { cls, label } = STATUS_MAP[status] ?? STATUS_MAP.clean
  return <span className={cls}>{label}</span>
}
