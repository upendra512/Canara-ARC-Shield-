import { Check } from 'lucide-react'

const audits = [
  {
    title: 'Q3 Internal Audit',
    date: 'Nov 2024',
    status: 'Completed',
  },
  {
    title: 'RBI Onsite Review',
    date: 'Dec 2024',
    status: 'Completed',
  },
]

export default function AuditTimeline() {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="mb-8 text-base font-bold text-brand-700">Audit Status Timeline</h2>

      <div className="relative px-2">
        <div className="absolute left-[calc(12.5%)] right-[calc(12.5%)] top-5 hidden h-px bg-slate-200 sm:block" />

        <div className="grid gap-8 sm:grid-cols-2 sm:gap-4">
          {audits.map((audit) => (
            <div key={audit.title} className="flex flex-col items-center text-center">
              <div className="relative z-10 flex h-10 w-10 items-center justify-center rounded-full bg-success">
                <Check className="h-5 w-5 text-white" strokeWidth={2.5} />
              </div>
              <p className="mt-3 text-xs font-medium text-slate-400">{audit.date}</p>
              <p className="mt-1 text-sm font-bold text-brand-700">{audit.title}</p>
              <p className="mt-1 flex items-center gap-1 text-xs font-medium text-success">
                <Check className="h-3 w-3" strokeWidth={2.5} />
                {audit.status}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
