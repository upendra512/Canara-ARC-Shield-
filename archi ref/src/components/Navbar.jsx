import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Search,
  MessageSquare,
  ShieldCheck,
  Users,
  Lock,
  Shield,
  Menu,
  X,
} from 'lucide-react'
import { useState } from 'react'

const navItems = [
  { to: '/', label: 'Executive Dashboard', icon: LayoutDashboard },
  { to: '/circular-explorer', label: 'Circular Explorer', icon: Search },
  { to: '/compliance-copilot', label: 'Compliance Copilot', icon: MessageSquare, badge: 'AI' },
  { to: '/blockchain-trust', label: 'Blockchain Trust Center', icon: ShieldCheck },
  { to: '/role-workspace', label: 'Role Workspace', icon: Users },
  { to: '/security-trust', label: 'Security & Trust', icon: Lock },
]

function NavItem({ to, label, icon: Icon, badge, onNavigate }) {
  return (
    <NavLink
      to={to}
      end={to === '/'}
      onClick={onNavigate}
      className={({ isActive }) =>
        [
          'group flex items-center gap-3 rounded-r-full px-4 py-2.5 text-sm font-medium transition-colors',
          isActive
            ? 'bg-brand-600 text-white'
            : 'text-slate-500 hover:bg-slate-50 hover:text-slate-700',
        ].join(' ')
      }
    >
      <Icon className="h-[18px] w-[18px] shrink-0" strokeWidth={1.75} />
      <span className="flex-1">{label}</span>
      {badge && (
        <span className="rounded bg-amber-100 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-amber-700">
          {badge}
        </span>
      )}
    </NavLink>
  )
}

export default function Navbar({ onNavigate }) {
  const [mobileOpen, setMobileOpen] = useState(false)

  const handleNavigate = () => {
    setMobileOpen(false)
    onNavigate?.()
  }

  const sidebarContent = (
    <>
      <div className="flex items-center gap-3 px-5 pb-6 pt-7">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-600">
          <Shield className="h-5 w-5 text-white" strokeWidth={2} />
        </div>
        <div>
          <p className="text-sm font-bold tracking-wide text-brand-700">ARC SHIELD</p>
          <p className="text-[11px] font-medium text-slate-400">CANARA BANK · V2.4.1</p>
        </div>
      </div>

      <p className="mb-2 px-5 text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-400">
        Platform
      </p>

      <nav className="flex flex-col gap-0.5 pr-3">
        {navItems.map((item) => (
          <NavItem key={item.to} {...item} onNavigate={handleNavigate} />
        ))}
      </nav>
    </>
  )

  return (
    <>
      {/* Mobile top bar */}
      <header className="fixed inset-x-0 top-0 z-40 flex h-14 items-center justify-between border-b border-slate-200 bg-white px-4 lg:hidden">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-brand-600">
            <Shield className="h-4 w-4 text-white" strokeWidth={2} />
          </div>
          <span className="text-sm font-bold text-brand-700">ARC SHIELD</span>
        </div>
        <button
          type="button"
          onClick={() => setMobileOpen(!mobileOpen)}
          className="rounded-lg p-2 text-slate-600 hover:bg-slate-100"
          aria-label={mobileOpen ? 'Close menu' : 'Open menu'}
        >
          {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </header>

      {/* Mobile drawer */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/40 lg:hidden"
          onClick={() => setMobileOpen(false)}
          aria-hidden="true"
        />
      )}
      <aside
        className={[
          'fixed inset-y-0 left-0 z-40 w-64 border-r border-slate-200 bg-white transition-transform duration-300 lg:translate-x-0',
          mobileOpen ? 'translate-x-0' : '-translate-x-full',
        ].join(' ')}
      >
        {sidebarContent}
      </aside>

      {/* Desktop sidebar spacer */}
      <div className="hidden w-64 shrink-0 lg:block" aria-hidden="true" />
    </>
  )
}

export { navItems }
