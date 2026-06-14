import PageTransition from '../components/PageTransition'

export default function PlaceholderPage({ title, description }) {
  return (
    <PageTransition>
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-brand-700 sm:text-3xl">{title}</h1>
        <p className="mt-1 text-sm text-slate-500">{description}</p>
      </header>
      <div className="rounded-xl border border-dashed border-slate-300 bg-white p-12 text-center">
        <p className="text-sm text-slate-400">This page will be built next.</p>
      </div>
    </PageTransition>
  )
}
