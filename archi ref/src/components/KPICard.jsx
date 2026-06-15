import { Award, TrendingUp, TrendingDown } from 'lucide-react'

function TrendBadge({ value, label, direction }) {
  const isUp = direction === 'up'
  const Icon = isUp ? TrendingUp : TrendingDown
  const colorClass = isUp ? 'text-success' : 'text-danger'

  return (
    <p className={`mt-2 flex items-center gap-1 text-xs font-medium ${colorClass}`}>
      <Icon className="h-3.5 w-3.5" strokeWidth={2.5} />
      <span>{value}</span>
      <span className="text-slate-400">{label}</span>
    </p>
  )
}

export default function KPICard({
  title,
  value,
  trend,
  trendLabel,
  trendDirection,
  accent = 'blue',
  icon: Icon = null,
  comparison,
  highlight,
  className = '',
}) {
  const accentColors = {
    blue: 'border-t-brand-600',
    orange: 'border-t-warning',
  }

  return (
    <div
      className={[
        'relative rounded-xl border border-slate-200 bg-white p-5 shadow-sm',
        accentColors[accent] || accentColors.blue,
        'border-t-[3px]',
        className,
      ].join(' ')}
    >
      <div className="flex items-start justify-between">
        <p className="text-[11px] font-semibold uppercase tracking-[0.08em] text-slate-400">
          {title}
        </p>
        {Icon && (
          <div className="rounded-lg bg-brand-50 p-2">
            <Icon className="h-4 w-4 text-brand-600" strokeWidth={1.75} />
          </div>
        )}
      </div>

      {comparison ? (
        <>
          <p className="mt-3 text-xs text-slate-400">
            <span className="line-through">{comparison.from}</span>
            <span className="mx-1.5 text-brand-600">→</span>
            <span className="font-medium text-brand-600">{comparison.to}</span>
          </p>
          <p className={`mt-1 text-2xl font-bold ${highlight || 'text-warning'}`}>{value}</p>
        </>
      ) : (
        <>
          <p className="mt-2 text-3xl font-bold text-brand-700">{value}</p>
          {trend && (
            <TrendBadge value={trend} label={trendLabel} direction={trendDirection} />
          )}
        </>
      )}
    </div>
  )
}
