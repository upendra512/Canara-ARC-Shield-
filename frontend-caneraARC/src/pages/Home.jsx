import { Award } from 'lucide-react'
import KPICard from '../components/KPICard'
import ComplianceGalaxy from '../components/ComplianceGalaxy'
import AuditTimeline from '../components/AuditTimeline'
import PageTransition, { FadeIn } from '../components/PageTransition'

export default function Home() {
  return (
    <PageTransition>
      <FadeIn>
        <header className="mb-6 lg:mb-8">
          <h1 className="text-2xl font-bold text-brand-700 sm:text-3xl">Executive Dashboard</h1>
          <p className="mt-1 text-sm text-slate-500">
            Good morning, Rajesh Kumar · Q1 FY2025 · 09:47 IST
          </p>
        </header>
      </FadeIn>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <FadeIn delay={0.05}>
          <KPICard
            title="Compliance Score"
            value="94.7%"
            trend="+2.3%"
            trendLabel="vs Q4 2024"
            trendDirection="up"
            accent="blue"
            icon={Award}
          />
        </FadeIn>
        <FadeIn delay={0.1}>
          <KPICard
            title="Pending Maps"
            value="23"
            trend="-5"
            trendLabel="from last month"
            trendDirection="down"
            accent="blue"
          />
        </FadeIn>
        <FadeIn delay={0.15}>
          <KPICard
            title="Circular Processing"
            value="99.7% Faster"
            accent="orange"
            comparison={{ from: '12 Hours', to: '< 2 Min' }}
            highlight="text-warning"
          />
        </FadeIn>
        <FadeIn delay={0.2}>
          <KPICard
            title="Compliance Mapping"
            value="90% Faster Audit"
            accent="blue"
            comparison={{ from: 'Manual Review', to: 'AI Automated' }}
            highlight="text-warning"
          />
        </FadeIn>
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <FadeIn delay={0.25}>
          <ComplianceGalaxy score={94.7} />
        </FadeIn>
        <FadeIn delay={0.3}>
          <AuditTimeline />
        </FadeIn>
      </div>
    </PageTransition>
  )
}
