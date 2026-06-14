const nodes = [
  { label: 'KYC', value: 97, status: 'compliant', angle: -90 },
  { label: 'AML', value: 91, status: 'warning', angle: -18 },
  { label: 'Cyber', value: 88, status: 'danger', angle: 54 },
  { label: 'Treasury', value: 95, status: 'compliant', angle: 126 },
  { label: 'Risk', value: 89, status: 'warning', angle: 198 },
]

const statusStyles = {
  compliant: 'border-success text-success',
  warning: 'border-warning text-warning',
  danger: 'border-danger text-danger',
}

const RADIUS = 130

function SatelliteNode({ label, value, status, angle, index }) {
  const rad = (angle * Math.PI) / 180
  const x = Math.cos(rad) * RADIUS
  const y = Math.sin(rad) * RADIUS

  return (
    <g style={{ animationDelay: `${index * 0.1}s` }}>
      <line
        x1="0"
        y1="0"
        x2={x}
        y2={y}
        stroke="#cbd5e1"
        strokeWidth="1"
        strokeDasharray="4 4"
      />
      <foreignObject x={x - 36} y={y - 36} width="72" height="72">
        <div
          className={[
            'flex h-[72px] w-[72px] flex-col items-center justify-center rounded-full border-2 bg-white shadow-sm',
            statusStyles[status],
          ].join(' ')}
        >
          <span className="text-[10px] font-semibold uppercase tracking-wide">{label}</span>
          <span className="text-sm font-bold">{value}%</span>
        </div>
      </foreignObject>
    </g>
  )
}

export default function ComplianceGalaxy({ score = 94.7 }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <h2 className="text-base font-bold text-brand-700">Compliance Galaxy</h2>
        <div className="flex items-center gap-4 text-xs text-slate-500">
          <span className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-success" />
            Compliant
          </span>
          <span className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-warning" />
            Warning
          </span>
        </div>
      </div>

      <div className="flex items-center justify-center overflow-hidden py-4">
        <svg
          viewBox="-200 -200 400 400"
          className="h-auto w-full max-w-[420px]"
          aria-label="Compliance galaxy visualization"
        >
          {nodes.map((node, i) => (
            <SatelliteNode key={node.label} {...node} index={i} />
          ))}
          <circle cx="0" cy="0" r="56" fill="#1e3a8a" />
          <text
            x="0"
            y="-4"
            textAnchor="middle"
            fill="white"
            fontSize="22"
            fontWeight="700"
            fontFamily="Inter, sans-serif"
          >
            {score}%
          </text>
          <text
            x="0"
            y="14"
            textAnchor="middle"
            fill="rgba(255,255,255,0.75)"
            fontSize="8"
            fontWeight="600"
            fontFamily="Inter, sans-serif"
            letterSpacing="1"
          >
            COMPLIANCE SCORE
          </text>
        </svg>
      </div>
    </div>
  )
}
