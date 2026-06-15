import { useState, useRef } from "react";
import {
  LayoutDashboard, Search, MessageSquare, ShieldCheck, Users,
  Lock, Bell, Settings, TrendingUp, TrendingDown, AlertTriangle,
  CheckCircle, FileText, Hash, Database, Send, RefreshCw,
  Download, ArrowRight, AlertCircle, Award, Zap, Building2,
  Globe, Fingerprint, GitBranch, ChevronRight, Eye, Cpu,
  Plus, Calendar, Filter,
} from "lucide-react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, AreaChart, Area,
} from "recharts";

const CB = "#004C97";
const CY = "#F7B731";
const OK = "#16a34a";
const WN = "#d97706";
const ER = "#dc2626";

const NAV = [
  { id: "dashboard", icon: LayoutDashboard, label: "Executive Dashboard" },
  { id: "circular",  icon: Search,          label: "Circular Explorer" },
  { id: "copilot",   icon: MessageSquare,   label: "Compliance Copilot", badge: "AI" },
  { id: "blockchain",icon: ShieldCheck,     label: "Blockchain Trust Center" },
  { id: "roles",     icon: Users,           label: "Role Workspace" },
  { id: "security",  icon: Lock,            label: "Security & Trust" },
];

/* ─── SIDEBAR ──────────────────────────────────────────────────────────── */

function Sidebar({ active, setActive }: { active: string; setActive: (s: string) => void }) {
  return (
    <aside className="w-[248px] h-screen flex flex-col border-r border-border bg-white shrink-0 select-none">
      <div className="h-16 flex items-center px-5 border-b border-border gap-3 shrink-0">
        <div className="w-9 h-9 rounded flex items-center justify-center shrink-0" style={{ background: CB }}>
          <ShieldCheck size={17} color="white" />
        </div>
        <div>
          <div className="font-extrabold text-[13px] tracking-wider leading-none" style={{ color: CB, fontFamily: "Barlow, sans-serif" }}>
            ARC SHIELD
          </div>
          <div className="text-[9px] text-muted-foreground mt-0.5 tracking-widest uppercase">Canara Bank · v2.4.1</div>
        </div>
      </div>

      <div className="px-4 pt-4 pb-1">
        <div className="text-[9px] font-bold text-muted-foreground uppercase tracking-widest">Platform</div>
      </div>

      <nav className="flex-1 px-2 space-y-0.5 overflow-y-auto">
        {NAV.map(({ id, icon: Icon, label, badge }) => {
          const on = active === id;
          return (
            <button
              key={id}
              onClick={() => setActive(id)}
              className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-md text-[12.5px] font-medium transition-all duration-100 text-left group ${
                on ? "text-white shadow-sm" : "text-muted-foreground hover:bg-secondary hover:text-foreground"
              }`}
              style={on ? { background: CB } : {}}
            >
              <Icon size={14} className={on ? "opacity-100" : "opacity-60 group-hover:opacity-90"} />
              <span className="flex-1" style={{ fontFamily: "Inter, sans-serif" }}>{label}</span>
              {badge && (
                <span className="text-[9px] font-extrabold px-1.5 py-0.5 rounded" style={{
                  background: on ? "rgba(255,255,255,0.2)" : `${CY}30`,
                  color: on ? "white" : "#7a5200",
                }}>
                  {badge}
                </span>
              )}
              {id === "dashboard" && !on && (
                <span className="w-1.5 h-1.5 rounded-full bg-red-500 shrink-0" />
              )}
            </button>
          );
        })}
      </nav>

      <div className="p-3 border-t border-border shrink-0">
        <div className="flex items-center gap-2.5 px-1.5 py-1.5 rounded-lg hover:bg-secondary cursor-pointer transition-colors">
          <div className="w-7 h-7 rounded-full flex items-center justify-center text-[10px] font-extrabold text-white shrink-0" style={{ background: CB }}>
            RK
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-[12px] font-semibold text-foreground truncate">Rajesh Kumar</div>
            <div className="text-[10px] text-muted-foreground">Compliance Officer</div>
          </div>
          <Settings size={12} className="text-muted-foreground shrink-0" />
        </div>
      </div>
    </aside>
  );
}

/* ─── PAGE HEADER ──────────────────────────────────────────────────────── */

function PageHeader({ title, sub, children }: { title: string; sub?: string; children?: React.ReactNode }) {
  return (
    <div className="h-14 border-b border-border flex items-center justify-between px-6 bg-white shrink-0">
      <div>
        <h1 className="text-[15px] font-extrabold leading-none" style={{ fontFamily: "Barlow, sans-serif", color: "#0a1628" }}>
          {title}
        </h1>
        {sub && <p className="text-[10.5px] text-muted-foreground mt-0.5">{sub}</p>}
      </div>
      <div className="flex items-center gap-2.5">
        {children}
        <div className="flex items-center gap-1.5 text-[10.5px] text-muted-foreground border border-border rounded px-2 py-1">
          <div className="w-1.5 h-1.5 rounded-full bg-green-500" />
          RBI Connected
        </div>
        <button className="relative p-1.5 rounded hover:bg-secondary transition-colors">
          <Bell size={14} className="text-muted-foreground" />
          <span className="absolute top-0.5 right-0.5 w-1.5 h-1.5 rounded-full bg-red-500" />
        </button>
      </div>
    </div>
  );
}

/* ─── KPI CARD ─────────────────────────────────────────────────────────── */

function KPICard({
  label, value, sub, trend, tv, color = CB, Icon,
}: {
  label: string; value: string; sub?: string; trend?: "up"|"dn"; tv?: string; color?: string; Icon?: React.FC<any>;
}) {
  return (
    <div className="bg-white rounded-lg border border-border p-4 relative overflow-hidden">
      <div className="absolute inset-x-0 top-0 h-0.5 rounded-t-lg" style={{ background: color }} />
      <div className="flex items-start justify-between">
        <span className="text-[9.5px] font-bold text-muted-foreground uppercase tracking-widest">{label}</span>
        {Icon && (
          <div className="w-7 h-7 rounded flex items-center justify-center" style={{ background: `${color}14` }}>
            <Icon size={13} style={{ color }} />
          </div>
        )}
      </div>
      <div className="mt-2 text-[30px] font-extrabold leading-none" style={{ fontFamily: "Barlow, sans-serif", color: "#0a1628" }}>
        {value}
      </div>
      {(sub || tv) && (
        <div className="mt-2 flex items-center gap-1.5">
          {tv && (
            <span className={`flex items-center gap-0.5 text-[11px] font-semibold ${trend === "up" ? "text-green-600" : "text-red-500"}`}>
              {trend === "up" ? <TrendingUp size={10} /> : <TrendingDown size={10} />}
              {tv}
            </span>
          )}
          {sub && <span className="text-[10.5px] text-muted-foreground">{sub}</span>}
        </div>
      )}
    </div>
  );
}

/* ─── COMPLIANCE GALAXY ────────────────────────────────────────────────── */

const GNODES = [
  { id: "KYC",      angle: -90, status: "compliant" as const, score: 97 },
  { id: "AML",      angle: -18, status: "warning"   as const, score: 91 },
  { id: "Cyber",    angle:  54, status: "violation" as const, score: 88 },
  { id: "Treasury", angle: 126, status: "compliant" as const, score: 95 },
  { id: "Risk",     angle: 198, status: "warning"   as const, score: 89 },
];
const SC = { compliant: OK, warning: WN, violation: ER };

function ComplianceGalaxy() {
  const R = 128, CX = 200, CY = 200;
  const xy = (a: number, r: number) => ({
    x: CX + r * Math.cos((a * Math.PI) / 180),
    y: CY + r * Math.sin((a * Math.PI) / 180),
  });

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-bold" style={{ fontFamily: "Barlow, sans-serif", color: "#0a1628" }}>
          Compliance Galaxy
        </h3>
        <div className="flex gap-3">
          {(["compliant", "warning", "violation"] as const).map(s => (
            <span key={s} className="flex items-center gap-1 text-[10px] text-muted-foreground capitalize">
              <span className="w-2 h-2 rounded-full" style={{ background: SC[s] }} />
              {s}
            </span>
          ))}
        </div>
      </div>
      <svg viewBox="0 0 400 400" className="w-full" style={{ maxHeight: 272 }}>
        <defs>
          <filter id="gsh">
            <feDropShadow dx="0" dy="2" stdDeviation="4" floodOpacity="0.11" />
          </filter>
          <radialGradient id="cgrad" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#0064c8" />
            <stop offset="100%" stopColor={CB} />
          </radialGradient>
        </defs>
        <circle cx={CX} cy={CY} r="158" fill="none" stroke="#eef3fb" strokeWidth="1" strokeDasharray="4 7" />
        <circle cx={CX} cy={CY} r="105" fill="none" stroke="#f0f5fc" strokeWidth="1" />
        {GNODES.map(n => {
          const p = xy(n.angle, R);
          return (
            <line key={n.id + "l"}
              x1={CX} y1={CY} x2={p.x} y2={p.y}
              stroke={SC[n.status]} strokeWidth="1.5" strokeOpacity="0.28"
              strokeDasharray={n.status === "violation" ? "5 3" : "none"}
            />
          );
        })}
        <circle cx={CX} cy={CY} r="60" fill="url(#cgrad)" filter="url(#gsh)" />
        <text x={CX} y={CY - 9} textAnchor="middle" fill="white" fontSize="21" fontWeight="800" fontFamily="Barlow, sans-serif">
          94.7%
        </text>
        <text x={CX} y={CY + 9} textAnchor="middle" fill="rgba(255,255,255,0.6)" fontSize="7.5" fontFamily="Inter, sans-serif" letterSpacing="1.8">
          COMPLIANCE SCORE
        </text>
        {GNODES.map(n => {
          const p = xy(n.angle, R);
          const c = SC[n.status];
          return (
            <g key={n.id}>
              <circle cx={p.x} cy={p.y} r="35" fill="white" stroke={c} strokeWidth="1.5" filter="url(#gsh)" />
              <text x={p.x} y={p.y - 7} textAnchor="middle" fill="#0a1628" fontSize="9.5" fontWeight="700" fontFamily="Barlow, sans-serif">
                {n.id}
              </text>
              <text x={p.x} y={p.y + 10} textAnchor="middle" fill={c} fontSize="14" fontWeight="800" fontFamily="Barlow, sans-serif">
                {n.score}%
              </text>
              <circle cx={p.x + 24} cy={p.y - 25} r="5" fill={c} />
            </g>
          );
        })}
      </svg>
    </div>
  );
}

/* ─── EXECUTIVE DASHBOARD ──────────────────────────────────────────────── */

const DEPT_DATA = [
  { name: "KYC",      score: 97, target: 95 },
  { name: "AML",      score: 91, target: 95 },
  { name: "Cyber",    score: 88, target: 90 },
  { name: "Treasury", score: 95, target: 92 },
  { name: "Risk",     score: 89, target: 90 },
  { name: "MSME",     score: 93, target: 92 },
];

const AUDIT_ITEMS = [
  { date: "Nov 2024", event: "Q3 Internal Audit",      status: "complete" },
  { date: "Dec 2024", event: "RBI Onsite Review",      status: "complete" },
  { date: "Jan 2025", event: "SEBI Compliance Check",  status: "active"   },
  { date: "Mar 2025", event: "Annual External Audit",  status: "pending"  },
];

function ExecutiveDashboard() {
  return (
    <div className="flex flex-col h-full overflow-auto">
      <PageHeader title="Executive Dashboard" sub="Good morning, Rajesh Kumar · Q1 FY2025 · 09:47 IST">
        <button className="flex items-center gap-1.5 text-[11.5px] px-3 py-1.5 rounded border border-border text-muted-foreground hover:bg-secondary transition-colors">
          <RefreshCw size={10} /> Refresh
        </button>
        <button className="flex items-center gap-1.5 text-[11.5px] px-3 py-1.5 rounded text-white transition-colors" style={{ background: CB }}>
          <Download size={10} /> Export
        </button>
      </PageHeader>

      <div className="p-6 space-y-5">
        {/* KPIs */}
        <div className="grid grid-cols-4 gap-4">
          <KPICard label="Compliance Score"   value="94.7%" tv="+2.3%"  trend="up" sub="vs Q4 2024"       color={CB}   Icon={Award} />
          <KPICard label="Pending MAPs"       value="23"    tv="-5"     trend="dn" sub="from last month"  color={WN}   Icon={AlertCircle} />
          <KPICard label="Active Circulars"   value="847"   tv="+12"    trend="up" sub="this month"       color={CB}   Icon={FileText} />
          <KPICard label="Risk Alerts"        value="7"     tv="-3"     trend="dn" sub="resolved today"   color={ER}   Icon={AlertTriangle} />
        </div>

        {/* Speed improvements */}
        <div className="grid grid-cols-3 gap-4">
          {[
            { label: "Circular Processing",  from: "12 Hours",      to: "< 2 Min",     perf: "99.7% Faster"      },
            { label: "Compliance Mapping",   from: "Manual Review", to: "AI Automated",perf: "90% Faster Audits" },
            { label: "RBI Reporting Lag",    from: "7 Days",        to: "Real-time",   perf: "100% On-time"      },
          ].map((c, i) => (
            <div key={i} className="bg-white border border-border rounded-lg p-4 relative overflow-hidden">
              <div className="absolute inset-x-0 top-0 h-0.5" style={{ background: i % 2 === 0 ? CY : CB }} />
              <div className="text-[9.5px] text-muted-foreground mb-2 font-bold uppercase tracking-widest">{c.label}</div>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-[11px] font-mono line-through text-muted-foreground">{c.from}</span>
                <ArrowRight size={9} style={{ color: CB }} />
                <span className="text-[11px] font-bold" style={{ color: CB }}>{c.to}</span>
              </div>
              <div className="text-[22px] font-extrabold leading-none" style={{ color: CY, fontFamily: "Barlow, sans-serif" }}>
                {c.perf}
              </div>
            </div>
          ))}
        </div>

        {/* Galaxy + Dept chart */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white border border-border rounded-lg p-5">
            <ComplianceGalaxy />
          </div>
          <div className="bg-white border border-border rounded-lg p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-bold" style={{ fontFamily: "Barlow, sans-serif", color: "#0a1628" }}>
                Department Performance
              </h3>
              <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
                <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-sm" style={{ background: CB }} />Score</span>
                <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-sm" style={{ background: CY }} />Target</span>
              </div>
            </div>
            <ResponsiveContainer width="100%" height={224}>
              <BarChart data={DEPT_DATA} barCategoryGap="30%">
                <CartesianGrid strokeDasharray="2 4" stroke="#eef3fa" vertical={false} />
                <XAxis dataKey="name" tick={{ fontSize: 11, fontFamily: "Inter, sans-serif", fill: "#5a6a85" }} axisLine={false} tickLine={false} />
                <YAxis domain={[80, 100]} tick={{ fontSize: 9.5, fontFamily: "JetBrains Mono, monospace", fill: "#5a6a85" }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ fontSize: 12, fontFamily: "Inter, sans-serif", border: `1px solid ${CB}22`, borderRadius: 6, boxShadow: "0 4px 16px rgba(0,0,0,0.08)" }} />
                <Bar dataKey="score"  name="Score"  fill={CB} radius={[3, 3, 0, 0]} />
                <Bar dataKey="target" name="Target" fill={CY} radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Audit timeline */}
        <div className="bg-white border border-border rounded-lg p-5">
          <h3 className="text-sm font-bold mb-6" style={{ fontFamily: "Barlow, sans-serif", color: "#0a1628" }}>
            Audit Status Timeline
          </h3>
          <div className="relative">
            <div className="absolute top-[9px] left-[12.5%] right-[12.5%] h-px" style={{ background: "#dae5f5" }} />
            <div className="grid grid-cols-4 gap-4">
              {AUDIT_ITEMS.map((item, i) => (
                <div key={i} className="flex flex-col items-center text-center">
                  <div className={`w-[18px] h-[18px] rounded-full border-2 z-10 flex items-center justify-center mb-2.5 ${
                    item.status === "complete" ? "border-green-500 bg-green-500" :
                    item.status === "active"   ? "bg-white" : "border-gray-200 bg-white"
                  }`} style={item.status === "active" ? { borderColor: CB } : {}}>
                    {item.status === "complete" && <CheckCircle size={10} color="white" />}
                    {item.status === "active"   && <div className="w-2.5 h-2.5 rounded-full" style={{ background: CB }} />}
                  </div>
                  <div className="text-[10px] text-muted-foreground">{item.date}</div>
                  <div className="text-[12px] font-semibold mt-0.5" style={{ color: "#0a1628", fontFamily: "Inter" }}>{item.event}</div>
                  <div className={`text-[10px] mt-1 font-semibold ${
                    item.status === "complete" ? "text-green-600" :
                    item.status === "active"   ? "text-blue-600"  : "text-muted-foreground"
                  }`}>
                    {item.status === "complete" ? "✓ Completed" : item.status === "active" ? "● In Progress" : "◌ Scheduled"}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ─── CIRCULAR EXPLORER ────────────────────────────────────────────────── */

const CIRCULARS = [
  { id: "RBI/2024/KYC/021",   title: "Know Your Customer (KYC) Guidelines — Enhanced Due Diligence",            reg: "RBI",  date: "2024-11-15", cat: "KYC",     status: "active",   sim: 85, simTo: "RBI KYC 2023",     clauses: 12, obs: 8  },
  { id: "RBI/2024/AML/009",   title: "Anti-Money Laundering Framework — Revised Reporting Thresholds",          reg: "RBI",  date: "2024-10-22", cat: "AML",     status: "active",   sim: 72, simTo: "RBI AML 2022",     clauses: 18, obs: 14 },
  { id: "SEBI/2024/CYBER/015",title: "Cybersecurity & Cyber Resilience Framework for Financial Entities",       reg: "SEBI", date: "2024-09-30", cat: "Cyber",   status: "warning",  sim: 61, simTo: "SEBI Cyber 2023",  clauses: 24, obs: 19 },
  { id: "RBI/2024/IT/042",    title: "IT Risk Management Guidelines — Cloud Infrastructure Controls",            reg: "RBI",  date: "2024-08-12", cat: "IT Risk", status: "active",   sim: 78, simTo: "RBI IT 2022",      clauses: 16, obs: 11 },
  { id: "RBI/2023/BASEL/018", title: "Basel III Capital Requirements — Updated Liquidity Coverage Ratio",       reg: "RBI",  date: "2023-12-01", cat: "Basel",   status: "complete", sim: 90, simTo: "Basel III 2022",   clauses: 31, obs: 22 },
];

type Circular = typeof CIRCULARS[0];

const CLAUSES_MOCK = [
  { id: "4.1", title: "Scope of Application",                  status: "mapped"   },
  { id: "4.2", title: "Enhanced Due Diligence Requirements",   status: "pending"  },
  { id: "4.3", title: "Beneficial Ownership Disclosure",       status: "mapped"   },
  { id: "5.1", title: "Customer Risk Categorization",          status: "flagged"  },
  { id: "5.2", title: "Periodic Review Timelines",             status: "mapped"   },
  { id: "6.1", title: "STR Filing Requirements",               status: "pending"  },
];

function CircularExplorer() {
  const [query, setQuery]     = useState("");
  const [reg, setReg]         = useState<string | null>(null);
  const [sel, setSel]         = useState<Circular | null>(null);
  const [view, setView]       = useState<"list"|"timeline">("list");

  const regs = ["RBI", "SEBI", "IRDAI", "MCA"];
  const filtered = CIRCULARS.filter(c => {
    const qm = !query || c.title.toLowerCase().includes(query.toLowerCase()) || c.id.toLowerCase().includes(query.toLowerCase());
    const rm = !reg || c.reg === reg;
    return qm && rm;
  });
  const statusColor: Record<string, string> = { active: CB, warning: WN, complete: OK };
  const statusLabel: Record<string, string> = { active: "Active", warning: "Action Needed", complete: "Compliant" };

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <PageHeader title="Circular Explorer" sub="847 circulars indexed · 23 regulators tracked">
        <button className="flex items-center gap-1.5 text-[11.5px] px-3 py-1.5 rounded border border-border text-muted-foreground hover:bg-secondary transition-colors">
          <Plus size={10} /> Import Circular
        </button>
      </PageHeader>

      <div className="flex-1 flex min-h-0">
        {/* Left list panel */}
        <div className="w-[380px] flex flex-col border-r border-border shrink-0">
          <div className="p-4 space-y-2.5 border-b border-border shrink-0">
            <div className="relative">
              <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
              <input
                value={query}
                onChange={e => setQuery(e.target.value)}
                placeholder="Search by ID, title, keyword..."
                className="w-full pl-8 pr-3 py-2 text-[12.5px] rounded border border-border bg-white focus:outline-none focus:ring-1 transition-shadow"
                style={{ fontFamily: "Inter, sans-serif" }}
              />
            </div>
            <div className="flex gap-1.5 flex-wrap">
              {[null, ...regs].map(r => (
                <button
                  key={r ?? "all"}
                  onClick={() => setReg(r)}
                  className={`px-2.5 py-1 rounded text-[10.5px] font-semibold transition-colors ${
                    reg === r ? "text-white" : "text-muted-foreground border border-border hover:bg-secondary"
                  }`}
                  style={reg === r ? { background: CB } : {}}
                >
                  {r ?? "All"}
                </button>
              ))}
              <button className="ml-auto px-2.5 py-1 rounded text-[10.5px] font-semibold border border-border text-muted-foreground hover:bg-secondary flex items-center gap-1">
                <Filter size={10} /> Filter
              </button>
            </div>
            <div className="flex gap-1.5">
              {(["list", "timeline"] as const).map(v => (
                <button
                  key={v}
                  onClick={() => setView(v)}
                  className={`flex-1 py-1.5 text-[10.5px] font-semibold rounded flex items-center justify-center gap-1.5 transition-colors ${
                    view === v ? "text-white" : "border border-border text-muted-foreground hover:bg-secondary"
                  }`}
                  style={view === v ? { background: CB } : {}}
                >
                  {v === "list" ? <><FileText size={10} /> List</> : <><Calendar size={10} /> Timeline</>}
                </button>
              ))}
            </div>
          </div>

          <div className="flex-1 overflow-y-auto">
            {filtered.length === 0 && (
              <div className="p-8 text-center text-muted-foreground text-sm">No circulars found</div>
            )}
            {filtered.map(c => (
              <button
                key={c.id}
                onClick={() => setSel(c)}
                className={`w-full text-left px-4 py-3.5 border-b border-border transition-colors hover:bg-secondary/50 ${
                  sel?.id === c.id ? "bg-secondary" : ""
                }`}
              >
                <div className="flex items-start justify-between gap-2 mb-1.5">
                  <span className="text-[10px] font-mono font-bold" style={{ color: CB }}>{c.id}</span>
                  <span className="text-[8.5px] font-extrabold px-1.5 py-0.5 rounded-sm uppercase tracking-wide text-white shrink-0"
                    style={{ background: statusColor[c.status] }}>
                    {statusLabel[c.status]}
                  </span>
                </div>
                <div className="text-[12px] font-semibold text-foreground leading-snug mb-2" style={{ fontFamily: "Inter" }}>{c.title}</div>
                <div className="flex items-center gap-3 text-[10px] text-muted-foreground mb-2">
                  <span>{c.date}</span>
                  <span>{c.clauses} clauses</span>
                  <span>{c.obs} obligations</span>
                </div>
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-[9.5px] text-muted-foreground">{c.sim}% similar to {c.simTo}</span>
                  </div>
                  <div className="w-full h-1 rounded-full bg-muted overflow-hidden">
                    <div className="h-full rounded-full transition-all"
                      style={{ width: `${c.sim}%`, background: c.sim > 80 ? ER : c.sim > 65 ? WN : CB }} />
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Detail panel */}
        <div className="flex-1 overflow-auto p-6">
          {!sel ? (
            <div className="h-full flex flex-col items-center justify-center text-center gap-3">
              <FileText size={40} className="text-muted-foreground/30" />
              <p className="text-sm text-muted-foreground">Select a circular to view its details, clause map, and similarity analysis</p>
            </div>
          ) : (
            <div className="space-y-5 max-w-3xl">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="text-[10.5px] font-mono font-bold mb-1" style={{ color: CB }}>{sel.id}</div>
                  <h2 className="text-[17px] font-extrabold leading-tight" style={{ fontFamily: "Barlow, sans-serif", color: "#0a1628" }}>
                    {sel.title}
                  </h2>
                  <div className="flex items-center gap-3 mt-2 text-[11.5px] text-muted-foreground flex-wrap">
                    <span className="font-bold" style={{ color: CB }}>{sel.reg}</span>
                    <span>{sel.date}</span>
                    <span>{sel.clauses} Clauses</span>
                    <span>{sel.obs} Obligations</span>
                    <span className="px-1.5 py-0.5 rounded text-[10px] font-bold" style={{ background: `${CB}12`, color: CB }}>{sel.cat}</span>
                  </div>
                </div>
                <div className="flex gap-2 shrink-0">
                  <button className="flex items-center gap-1.5 text-[11.5px] px-3 py-1.5 rounded border border-border text-muted-foreground hover:bg-secondary">
                    <GitBranch size={10} /> Compare
                  </button>
                  <button className="flex items-center gap-1.5 text-[11.5px] px-3 py-1.5 rounded text-white" style={{ background: CB }}>
                    <Eye size={10} /> View MAP
                  </button>
                </div>
              </div>

              {/* Similarity banner */}
              <div className="rounded-lg p-4 border" style={{ background: `${CY}0e`, borderColor: `${CY}50` }}>
                <div className="flex items-center gap-4 mb-3">
                  <div className="text-[28px] font-extrabold leading-none" style={{ color: "#7a5200", fontFamily: "Barlow, sans-serif" }}>
                    {sel.sim}%
                  </div>
                  <div>
                    <div className="text-[13px] font-bold text-foreground">Similar to {sel.simTo}</div>
                    <div className="text-[11px] text-muted-foreground mt-0.5">
                      Existing compliance obligations may apply — review before creating new MAPs
                    </div>
                  </div>
                </div>
                <div className="w-full h-2 rounded-full bg-white border border-border overflow-hidden">
                  <div className="h-full rounded-full" style={{ width: `${sel.sim}%`, background: CY }} />
                </div>
              </div>

              {/* Clause viewer */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-bold" style={{ fontFamily: "Barlow, sans-serif", color: "#0a1628" }}>Clause Overview</h3>
                  <span className="text-[10px] text-muted-foreground">{sel.clauses} total · 4 mapped · 2 pending</span>
                </div>
                <div className="space-y-1.5">
                  {CLAUSES_MOCK.map(clause => (
                    <div key={clause.id}
                      className="flex items-center gap-3 px-3.5 py-2.5 rounded-md border border-border bg-white hover:bg-secondary/30 cursor-pointer transition-colors">
                      <span className="font-mono text-[10.5px] font-bold w-7 shrink-0" style={{ color: CB }}>§{clause.id}</span>
                      <span className="text-[12.5px] flex-1" style={{ fontFamily: "Inter" }}>{clause.title}</span>
                      <span className={`text-[9.5px] font-bold px-2 py-0.5 rounded ${
                        clause.status === "mapped"   ? "text-green-700 bg-green-50 border border-green-200" :
                        clause.status === "pending"  ? "text-amber-700 bg-amber-50 border border-amber-200" :
                                                       "text-red-700 bg-red-50 border border-red-200"
                      }`}>
                        {clause.status.toUpperCase()}
                      </span>
                      <ChevronRight size={12} className="text-muted-foreground" />
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/* ─── COMPLIANCE COPILOT ────────────────────────────────────────────────── */

type Msg = { role: "user"|"ai"; text: string; sources?: string[]; time: string };

const INIT_MSGS: Msg[] = [
  {
    role: "ai",
    text: "Hello, Rajesh. I'm ARC Shield AI — your compliance copilot powered by Canara Bank's proprietary regulatory knowledge graph.\n\nI have access to 847 indexed circulars, 23 active MAPs, and your organisation's full compliance history. How can I assist you today?",
    sources: [],
    time: "09:45 AM",
  },
  {
    role: "user",
    text: "Explain Clause 4.2 of RBI/2024/KYC/021",
    time: "09:46 AM",
  },
  {
    role: "ai",
    text: "Clause 4.2 — Enhanced Due Diligence Requirements (RBI/2024/KYC/021)\n\nThis clause mandates Enhanced Due Diligence (EDD) for all Politically Exposed Persons (PEPs), high-risk customers, and transactions from FATF-flagged jurisdictions. Key requirements:\n\n• Senior management approval for onboarding PEPs\n• Source of funds documentation for transactions > ₹10 lakh\n• Quarterly review of high-risk accounts (previously semi-annual)\n• Real-time STR filing for suspicious transactions > ₹50 lakh\n\nYour current compliance status: 6 of 8 obligations mapped. 2 pending implementation by 31 Jan 2025.",
    sources: ["RBI/2024/KYC/021 §4.2", "FATF Guidance 2024", "PMLA Rules 2005 §11"],
    time: "09:46 AM",
  },
];

const QUICK_PROMPTS = [
  "Explain Clause 4.2", "Compare two circulars", "Show pending obligations",
  "Summarize KYC regulations", "Why was this flagged?", "Generate MAP for AML/009",
];

function ComplianceCopilot() {
  const [msgs, setMsgs] = useState<Msg[]>(INIT_MSGS);
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  const send = (text: string) => {
    if (!text.trim()) return;
    const t = new Date().toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" });
    const reply: Msg = {
      role: "ai",
      text: `Analysing: "${text.trim()}"\n\nConnecting to the ARC Shield knowledge graph across 847 circulars and your compliance history. In production this invokes a multi-hop reasoning chain across RBI, SEBI, IRDAI, and MCA circulars with blockchain-verified evidence references.`,
      sources: ["Knowledge Graph v4.2", "Compliance DB 2025"],
      time: t,
    };
    setMsgs(p => [...p, { role: "user", text: text.trim(), time: t }, reply]);
    setInput("");
    setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }), 80);
  };

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <PageHeader title="Compliance Copilot" sub="Ask ARC Shield · Powered by Canara Regulatory AI v4.2">
        <div className="flex items-center gap-1.5 text-[10.5px] px-2 py-1 rounded font-semibold"
          style={{ background: `${CY}22`, color: "#7a5200" }}>
          <Zap size={10} /> ARC-7 Turbo
        </div>
      </PageHeader>

      <div className="flex flex-1 min-h-0">
        {/* Chat */}
        <div className="flex-1 flex flex-col min-h-0">
          <div className="flex-1 overflow-y-auto px-6 py-5 space-y-5">
            {msgs.map((m, i) => (
              <div key={i} className={`flex gap-2.5 ${m.role === "user" ? "flex-row-reverse" : ""}`}>
                <div className={`w-7 h-7 rounded-full flex items-center justify-center text-[9.5px] font-extrabold shrink-0 text-white`}
                  style={{ background: m.role === "ai" ? CB : "#64748b" }}>
                  {m.role === "ai" ? "AI" : "RK"}
                </div>
                <div className={`max-w-[76%] flex flex-col gap-1.5 ${m.role === "user" ? "items-end" : "items-start"}`}>
                  <div className={`rounded-xl px-4 py-3 text-[12.5px] leading-relaxed ${
                    m.role === "user" ? "text-white rounded-tr-sm" : "bg-white border border-border text-foreground rounded-tl-sm"
                  }`} style={{
                    background: m.role === "user" ? CB : undefined,
                    fontFamily: "Inter, sans-serif",
                    whiteSpace: "pre-line",
                  }}>
                    {m.text}
                  </div>
                  {m.sources && m.sources.length > 0 && (
                    <div className="flex gap-1.5 flex-wrap">
                      {m.sources.map(s => (
                        <span key={s} className="text-[9.5px] px-2 py-0.5 rounded-full border font-mono"
                          style={{ borderColor: `${CB}35`, color: CB, background: `${CB}08` }}>
                          {s}
                        </span>
                      ))}
                    </div>
                  )}
                  <span className="text-[9.5px] text-muted-foreground">{m.time}</span>
                </div>
              </div>
            ))}
            <div ref={bottomRef} />
          </div>

          <div className="px-6 pb-2">
            <div className="flex gap-1.5 flex-wrap">
              {QUICK_PROMPTS.map(p => (
                <button key={p} onClick={() => send(p)}
                  className="text-[10.5px] px-3 py-1 rounded-full border border-border text-muted-foreground hover:bg-secondary hover:text-foreground transition-colors">
                  {p}
                </button>
              ))}
            </div>
          </div>

          <div className="px-6 pb-6 pt-2">
            <div className="flex gap-2 p-1 border border-border rounded-xl bg-white focus-within:ring-1 transition-shadow"
              style={{}}>
              <input
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === "Enter" && !e.shiftKey && (e.preventDefault(), send(input))}
                placeholder="Ask about any circular, obligation, or compliance requirement..."
                className="flex-1 px-3 py-2.5 text-[12.5px] bg-transparent focus:outline-none"
                style={{ fontFamily: "Inter" }}
              />
              <button onClick={() => send(input)} disabled={!input.trim()}
                className="w-9 h-9 rounded-lg flex items-center justify-center m-0.5 transition-opacity disabled:opacity-30"
                style={{ background: CB }}>
                <Send size={13} color="white" />
              </button>
            </div>
            <p className="text-[9.5px] text-muted-foreground mt-1.5 text-center">
              ARC Shield AI · Responses based on indexed RBI/SEBI/IRDAI circulars · Not legal advice
            </p>
          </div>
        </div>

        {/* Sources sidebar */}
        <div className="w-60 border-l border-border flex flex-col bg-white shrink-0">
          <div className="px-4 py-3 border-b border-border shrink-0">
            <h3 className="text-[11px] font-bold text-foreground" style={{ fontFamily: "Barlow" }}>Evidence & Sources</h3>
          </div>
          <div className="flex-1 overflow-y-auto p-3.5 space-y-2.5">
            {[
              { ref: "RBI/2024/KYC/021", clause: "§4.2", conf: 98 },
              { ref: "PMLA Rules 2005",  clause: "§11",  conf: 94 },
              { ref: "FATF Guidance 2024",clause: "R.12", conf: 91 },
              { ref: "RBI/2023/AML/009", clause: "§7.1", conf: 87 },
              { ref: "RBI/2022/IT/031",  clause: "§3.5", conf: 82 },
            ].map((item, i) => (
              <div key={i} className="p-2.5 rounded-lg border border-border bg-secondary/30">
                <div className="flex items-start justify-between mb-1">
                  <span className="text-[9.5px] font-mono font-bold leading-tight" style={{ color: CB }}>{item.ref}</span>
                  <span className="text-[9.5px] font-bold" style={{ color: OK }}>{item.conf}%</span>
                </div>
                <div className="text-[9.5px] text-muted-foreground mb-1.5">Clause {item.clause}</div>
                <div className="w-full h-1 rounded-full bg-muted overflow-hidden">
                  <div className="h-full rounded-full" style={{ width: `${item.conf}%`, background: CB }} />
                </div>
              </div>
            ))}
          </div>
          <div className="p-3.5 border-t border-border shrink-0">
            <div className="flex items-center gap-2 text-[10px]">
              <div className="w-5 h-5 rounded flex items-center justify-center" style={{ background: `${OK}18` }}>
                <ShieldCheck size={10} style={{ color: OK }} />
              </div>
              <span className="text-muted-foreground">Blockchain-verified evidence</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ─── BLOCKCHAIN TRUST CENTER ──────────────────────────────────────────── */

const HASH_CARDS = [
  { label: "Circular Hash",  id: "CIR-2024-11-15",    hash: "0x3f8a9b2c4e1d7f6a...a8b3c2", Icon: FileText,  color: CB   },
  { label: "MAP Hash",       id: "MAP-KYC-021-A3",    hash: "0xa1c4e7f2b9d3e5c8...f2a1b4", Icon: GitBranch, color: CB   },
  { label: "Evidence Hash",  id: "EVD-20241115-089",  hash: "0x7d2b8f1e3c5a9d4b...e7f3a2", Icon: Database,  color: WN   },
  { label: "Audit Receipt",  id: "AUD-Q3-2024-RBI",   hash: "0x9e3c5a8b2f4d1c7e...b5a9c3", Icon: Award,     color: OK   },
];

const CHAIN_EVENTS = [
  { time: "09:15:42", event: "Circular Ingested",       hash: "0x3f8a...a8b3", node: "Node-1", ok: true },
  { time: "09:15:43", event: "AI Analysis Complete",    hash: "0x7d2b...e7f3", node: "Node-3", ok: true },
  { time: "09:16:01", event: "MAP Generated",           hash: "0xa1c4...f2a1", node: "Node-2", ok: true },
  { time: "09:18:22", event: "Officer Review & Sign",   hash: "0x5b9e...c4d2", node: "Node-1", ok: true },
  { time: "09:21:05", event: "Evidence Locked",         hash: "0x9e3c...b5a9", node: "Node-4", ok: true },
  { time: "09:21:06", event: "Audit Receipt Issued",    hash: "0x2f7a...d8e1", node: "Node-2", ok: true },
];

function BlockchainTrustCenter() {
  const [selHash, setSelHash] = useState(HASH_CARDS[0]);

  return (
    <div className="flex flex-col h-full overflow-auto">
      <PageHeader title="Blockchain Trust Center" sub="Hyperledger Fabric · 4 Nodes Active · Last block: 3s ago">
        <div className="flex items-center gap-1.5 text-[10.5px] text-green-700 px-2 py-1 rounded font-semibold"
          style={{ background: `${OK}12` }}>
          <div className="w-1.5 h-1.5 rounded-full bg-green-500" />
          Network Healthy
        </div>
      </PageHeader>

      <div className="p-6 space-y-5">
        {/* Hash cards */}
        <div className="grid grid-cols-4 gap-4">
          {HASH_CARDS.map((c, i) => {
            const Icon = c.Icon;
            const on = selHash.label === c.label;
            return (
              <button key={i} onClick={() => setSelHash(c)}
                className={`text-left rounded-lg border p-4 transition-all ${
                  on ? "border-2 shadow-sm" : "border-border bg-white hover:bg-secondary/30"
                }`}
                style={on ? { borderColor: c.color, background: `${c.color}06` } : {}}>
                <div className="flex items-center justify-between mb-3">
                  <div className="w-8 h-8 rounded-md flex items-center justify-center" style={{ background: `${c.color}14` }}>
                    <Icon size={14} style={{ color: c.color }} />
                  </div>
                  <CheckCircle size={13} style={{ color: OK }} />
                </div>
                <div className="text-[9.5px] text-muted-foreground uppercase tracking-widest font-bold mb-1">{c.label}</div>
                <div className="text-[10px] font-mono font-bold truncate mb-0.5" style={{ color: c.color }}>{c.hash}</div>
                <div className="text-[9.5px] text-muted-foreground">{c.id}</div>
              </button>
            );
          })}
        </div>

        <div className="grid grid-cols-[1fr_280px] gap-4">
          {/* Chain of Custody */}
          <div className="bg-white border border-border rounded-lg p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-bold" style={{ fontFamily: "Barlow, sans-serif", color: "#0a1628" }}>Chain of Custody</h3>
              <span className="text-[10.5px] text-muted-foreground font-mono">{CHAIN_EVENTS.length} events · Block #49,221</span>
            </div>
            <div className="relative">
              <div className="absolute left-[9px] top-3 bottom-1 w-0.5" style={{ background: "#dae5f5" }} />
              <div className="space-y-4">
                {CHAIN_EVENTS.map((ev, i) => (
                  <div key={i} className="flex gap-4 items-start">
                    <div className="w-[18px] h-[18px] rounded-full border-2 shrink-0 z-10 flex items-center justify-center bg-white"
                      style={{ borderColor: OK }}>
                      <div className="w-2 h-2 rounded-full" style={{ background: OK }} />
                    </div>
                    <div className="flex-1 pb-0.5">
                      <div className="flex items-center justify-between">
                        <span className="text-[12.5px] font-semibold text-foreground" style={{ fontFamily: "Inter" }}>{ev.event}</span>
                        <span className="text-[10px] text-muted-foreground font-mono">{ev.time}</span>
                      </div>
                      <div className="flex items-center gap-3 mt-0.5">
                        <span className="font-mono text-[10px]" style={{ color: CB }}>{ev.hash}</span>
                        <span className="text-[10px] text-muted-foreground">{ev.node}</span>
                        <span className="text-[9.5px] font-bold text-green-600">✓ Verified</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right panels */}
          <div className="space-y-4">
            <div className="bg-white border border-border rounded-lg p-4">
              <h3 className="text-[11px] font-bold mb-3" style={{ fontFamily: "Barlow", color: "#0a1628" }}>X.509 Signatures</h3>
              <div className="space-y-2">
                {[
                  { name: "Rajesh Kumar",  role: "Compliance Officer" },
                  { name: "Priya Sharma",  role: "Deputy CGM" },
                  { name: "ARC Shield AI", role: "System Attestation" },
                ].map((s, i) => (
                  <div key={i} className="flex items-center gap-2.5 py-1.5 border-b border-border last:border-0">
                    <div className="w-6 h-6 rounded-full text-[9.5px] font-extrabold flex items-center justify-center text-white shrink-0"
                      style={{ background: CB }}>
                      {s.name.split(" ").map(w => w[0]).join("").slice(0, 2)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-[11px] font-semibold truncate">{s.name}</div>
                      <div className="text-[9.5px] text-muted-foreground">{s.role}</div>
                    </div>
                    <CheckCircle size={12} style={{ color: OK }} />
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white border border-border rounded-lg p-4">
              <h3 className="text-[11px] font-bold mb-3" style={{ fontFamily: "Barlow", color: "#0a1628" }}>Fabric Network</h3>
              <div className="space-y-2">
                {[
                  { node: "Node-1", org: "Canara HO",     txns: 1247 },
                  { node: "Node-2", org: "RBI Observer",  txns: 1247 },
                  { node: "Node-3", org: "SEBI Observer", txns: 1244 },
                  { node: "Node-4", org: "Orderer",       txns: 1247 },
                ].map((n, i) => (
                  <div key={i} className="flex items-center gap-2">
                    <div className="w-1.5 h-1.5 rounded-full shrink-0" style={{ background: OK }} />
                    <div className="flex-1 text-[11px] font-semibold">{n.node}</div>
                    <div className="text-[10px] text-muted-foreground font-mono">{n.txns.toLocaleString()}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Transactions table */}
        <div className="bg-white border border-border rounded-lg p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold" style={{ fontFamily: "Barlow, sans-serif", color: "#0a1628" }}>Recent Fabric Transactions</h3>
            <button className="text-[10.5px] px-2.5 py-1 border border-border rounded text-muted-foreground hover:bg-secondary">View All</button>
          </div>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                {["Txn ID", "Function", "Channel", "Block", "Time", "Status"].map(h => (
                  <th key={h} className="text-left pb-2 text-[9.5px] font-bold text-muted-foreground uppercase tracking-widest pr-4">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {[
                { id: "tx_9e3c5a...", fn: "StoreCircularHash",    ch: "compliance-channel", block: 49221, time: "09:21:06" },
                { id: "tx_7d2b8f...", fn: "LockEvidenceHash",     ch: "evidence-channel",   block: 49220, time: "09:21:05" },
                { id: "tx_a1c4e7...", fn: "RecordMAPApproval",    ch: "compliance-channel", block: 49219, time: "09:18:22" },
                { id: "tx_5b9e2c...", fn: "GenerateAuditReceipt", ch: "audit-channel",      block: 49215, time: "09:16:01" },
              ].map((tx, i) => (
                <tr key={i} className="hover:bg-secondary/30 transition-colors">
                  <td className="py-2 pr-4 font-mono text-[10.5px]" style={{ color: CB }}>{tx.id}</td>
                  <td className="py-2 pr-4 text-[12px] font-medium">{tx.fn}</td>
                  <td className="py-2 pr-4 text-[10.5px] text-muted-foreground font-mono">{tx.ch}</td>
                  <td className="py-2 pr-4 text-[10.5px] font-mono text-muted-foreground">{tx.block}</td>
                  <td className="py-2 pr-4 text-[10.5px] text-muted-foreground font-mono">{tx.time}</td>
                  <td className="py-2">
                    <span className="text-[9.5px] font-extrabold text-green-700 bg-green-50 border border-green-200 px-2 py-0.5 rounded">
                      COMMITTED
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

/* ─── ROLE WORKSPACE ────────────────────────────────────────────────────── */

const ROLES = [
  { id: "compliance", label: "Compliance Officer", Icon: ShieldCheck },
  { id: "it",         label: "IT Team",            Icon: Cpu        },
  { id: "cxo",        label: "CXO View",           Icon: Award      },
  { id: "auditor",    label: "Auditor / RBI",      Icon: Eye        },
];

function ComplianceOfficerView() {
  return (
    <div className="space-y-5">
      <div className="grid grid-cols-[1fr_260px] gap-4">
        <div className="bg-white border border-border rounded-lg p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold" style={{ fontFamily: "Barlow", color: "#0a1628" }}>My Pending MAPs (23)</h3>
            <button className="flex items-center gap-1.5 text-[11.5px] px-3 py-1.5 rounded text-white" style={{ background: CB }}>
              <Plus size={10} /> New MAP
            </button>
          </div>
          <div className="space-y-2">
            {[
              { id: "MAP-KYC-021-A3", circ: "RBI/2024/KYC/021",    dl: "2025-01-31", priority: "High"     },
              { id: "MAP-AML-009-B1", circ: "RBI/2024/AML/009",    dl: "2025-02-15", priority: "Medium"   },
              { id: "MAP-CYB-015-C2", circ: "SEBI/2024/CYBER/015", dl: "2025-01-20", priority: "Critical" },
              { id: "MAP-IT-042-D1",  circ: "RBI/2024/IT/042",     dl: "2025-02-28", priority: "Medium"   },
            ].map(m => (
              <div key={m.id}
                className="flex items-center gap-4 px-3.5 py-2.5 rounded-md border border-border hover:bg-secondary/30 transition-colors cursor-pointer">
                <span className="font-mono text-[10.5px] font-bold shrink-0" style={{ color: CB }}>{m.id}</span>
                <span className="flex-1 text-[12px] text-muted-foreground">{m.circ}</span>
                <span className="text-[10.5px] font-mono text-muted-foreground shrink-0">{m.dl}</span>
                <span className={`text-[9.5px] font-extrabold px-2 py-0.5 rounded shrink-0 ${
                  m.priority === "Critical" ? "text-red-700 bg-red-50 border border-red-200" :
                  m.priority === "High"     ? "text-amber-700 bg-amber-50 border border-amber-200" :
                                              "text-blue-700 bg-blue-50 border border-blue-200"
                }`}>{m.priority}</span>
                <ChevronRight size={11} className="text-muted-foreground shrink-0" />
              </div>
            ))}
          </div>
        </div>
        <div className="space-y-4">
          <div className="bg-white border border-border rounded-lg p-4">
            <h3 className="text-[11px] font-bold mb-3" style={{ fontFamily: "Barlow", color: "#0a1628" }}>Obligation Tracker</h3>
            {[
              { label: "Mapped",      value: 186, color: OK   },
              { label: "In Progress", value: 38,  color: WN   },
              { label: "Overdue",     value: 7,   color: ER   },
            ].map(item => (
              <div key={item.label} className="flex items-center justify-between py-2 border-b border-border last:border-0">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-sm" style={{ background: item.color }} />
                  <span className="text-[12px] text-foreground">{item.label}</span>
                </div>
                <span className="font-mono text-[14px] font-extrabold" style={{ color: item.color }}>{item.value}</span>
              </div>
            ))}
          </div>
          <div className="bg-white border border-border rounded-lg p-4">
            <h3 className="text-[11px] font-bold mb-3" style={{ fontFamily: "Barlow", color: "#0a1628" }}>Quick Actions</h3>
            <div className="space-y-2">
              {[
                { label: "Run AI Scan",     Icon: Zap      },
                { label: "Export Report",   Icon: Download },
                { label: "View Audit Log",  Icon: Eye      },
              ].map(a => (
                <button key={a.label}
                  className="w-full flex items-center gap-2 px-3 py-2 rounded-md border border-border text-[12px] font-medium text-foreground hover:bg-secondary transition-colors">
                  <a.Icon size={11} style={{ color: CB }} />
                  {a.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function ITTeamView() {
  return (
    <div className="space-y-5">
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: "API Uptime",         value: "99.98%",  ok: true  },
          { label: "Blockchain Nodes",   value: "4/4",     ok: true  },
          { label: "AI Engine",          value: "Healthy", ok: true  },
          { label: "DB Connections",     value: "142/200", ok: false },
        ].map((s, i) => (
          <div key={i} className="bg-white border border-border rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[9.5px] text-muted-foreground uppercase tracking-widest font-bold">{s.label}</span>
              <div className={`w-2 h-2 rounded-full ${s.ok ? "bg-green-500" : "bg-amber-500"}`} />
            </div>
            <div className="text-[22px] font-extrabold" style={{ fontFamily: "Barlow", color: s.ok ? OK : WN }}>{s.value}</div>
          </div>
        ))}
      </div>
      <div className="bg-white border border-border rounded-lg p-5">
        <h3 className="text-sm font-bold mb-4" style={{ fontFamily: "Barlow", color: "#0a1628" }}>System Health Log</h3>
        <div className="space-y-0.5 font-mono text-[11px]">
          {[
            { time: "09:47:12", msg: "[INFO]  Circular ingestion pipeline: 12 docs processed",    level: "info" },
            { time: "09:46:55", msg: "[OK]    Blockchain Node-3 reconnected after 2s timeout",    level: "ok"   },
            { time: "09:45:30", msg: "[WARN]  DB connection pool at 71% capacity",                level: "warn" },
            { time: "09:44:18", msg: "[INFO]  AI model ARC-7-Turbo responded in 1.2s avg",       level: "info" },
            { time: "09:43:05", msg: "[OK]    RBI API handshake successful · TLS 1.3",           level: "ok"   },
            { time: "09:41:52", msg: "[INFO]  Scheduled audit batch: 23 MAPs queued",            level: "info" },
          ].map((log, i) => (
            <div key={i} className={`flex gap-4 py-2 px-3 rounded ${
              log.level === "warn" ? "text-amber-700 bg-amber-50" :
              log.level === "ok"   ? "text-green-700 bg-green-50/50" :
                                     "text-muted-foreground"
            }`}>
              <span className="shrink-0 opacity-70">{log.time}</span>
              <span>{log.msg}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function CXOView() {
  const trendData = [
    { m: "Aug", score: 89 }, { m: "Sep", score: 91 }, { m: "Oct", score: 90 },
    { m: "Nov", score: 93 }, { m: "Dec", score: 92 }, { m: "Jan", score: 94.7 },
  ];
  return (
    <div className="space-y-5">
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: "Overall Compliance",            value: "94.7%",  note: "Exceeds 90% RBI benchmark",  hi: true  },
          { label: "Pending Regulatory Actions",    value: "23",     note: "Target: <15 by Q2 FY25",     hi: false },
          { label: "Blockchain Proof Completeness", value: "100%",   note: "Full audit trail coverage",  hi: true  },
        ].map((item, i) => (
          <div key={i} className="bg-white border border-border rounded-lg p-5 relative overflow-hidden">
            <div className="absolute inset-x-0 top-0 h-0.5" style={{ background: i === 1 ? WN : CB }} />
            <div className="text-[9.5px] text-muted-foreground uppercase tracking-widest font-bold mb-2">{item.label}</div>
            <div className="text-[32px] font-extrabold leading-none" style={{ fontFamily: "Barlow", color: "#0a1628" }}>{item.value}</div>
            <div className="text-[11px] text-muted-foreground mt-1.5">{item.note}</div>
          </div>
        ))}
      </div>
      <div className="bg-white border border-border rounded-lg p-5">
        <h3 className="text-sm font-bold mb-4" style={{ fontFamily: "Barlow", color: "#0a1628" }}>6-Month Compliance Trend</h3>
        <ResponsiveContainer width="100%" height={200}>
          <AreaChart data={trendData}>
            <defs>
              <linearGradient id="sg" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor={CB} stopOpacity={0.13} />
                <stop offset="95%" stopColor={CB} stopOpacity={0}    />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="2 4" stroke="#eef3fa" vertical={false} />
            <XAxis dataKey="m" tick={{ fontSize: 11, fontFamily: "Inter", fill: "#5a6a85" }} axisLine={false} tickLine={false} />
            <YAxis domain={[85, 100]} tick={{ fontSize: 10, fontFamily: "JetBrains Mono", fill: "#5a6a85" }} axisLine={false} tickLine={false} />
            <Tooltip contentStyle={{ fontSize: 12, fontFamily: "Inter", borderRadius: 6, border: `1px solid ${CB}22` }} />
            <Area type="monotone" dataKey="score" stroke={CB} strokeWidth={2.5} fill="url(#sg)" dot={{ fill: CB, r: 3 }} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function AuditorView() {
  return (
    <div className="space-y-5">
      <div className="bg-white border border-border rounded-lg p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-bold" style={{ fontFamily: "Barlow", color: "#0a1628" }}>Audit Evidence Package</h3>
          <button className="flex items-center gap-1.5 text-[11.5px] px-3 py-1.5 rounded text-white" style={{ background: CB }}>
            <Download size={10} /> Download Package
          </button>
        </div>
        <div className="grid grid-cols-4 gap-3">
          {[
            { label: "Circulars Indexed", value: "847"   },
            { label: "MAPs Verified",     value: "231"   },
            { label: "Evidence Items",    value: "1,429" },
            { label: "Blockchain Receipts", value: "231" },
          ].map((item, i) => (
            <div key={i} className="border border-border rounded-lg p-3.5 bg-secondary/20 text-center">
              <div className="text-[9.5px] text-muted-foreground uppercase tracking-widest font-bold mb-2">{item.label}</div>
              <div className="text-[22px] font-extrabold" style={{ fontFamily: "Barlow", color: "#0a1628" }}>{item.value}</div>
              <div className="flex items-center justify-center gap-1 mt-1.5">
                <CheckCircle size={10} style={{ color: OK }} />
                <span className="text-[9.5px] text-green-600 font-semibold">Verified</span>
              </div>
            </div>
          ))}
        </div>
      </div>
      <div className="bg-white border border-border rounded-lg p-5">
        <h3 className="text-sm font-bold mb-4" style={{ fontFamily: "Barlow", color: "#0a1628" }}>RBI Audit Trail</h3>
        <div className="space-y-1.5">
          {[
            { action: "KYC Policy Updated",      user: "Rajesh Kumar", date: "2025-01-10", hash: "0x3f8a...a8b3" },
            { action: "AML Threshold Changed",   user: "Priya Sharma", date: "2025-01-08", hash: "0x7d2b...e7f3" },
            { action: "Cyber MAP Approved",      user: "Rajesh Kumar", date: "2025-01-05", hash: "0xa1c4...f2a1" },
            { action: "Q3 Audit Submitted",      user: "System",       date: "2024-12-30", hash: "0x9e3c...b5a9" },
          ].map((item, i) => (
            <div key={i}
              className="grid gap-4 items-center px-3.5 py-2.5 rounded-md border border-border hover:bg-secondary/30 transition-colors text-[12px]"
              style={{ gridTemplateColumns: "2fr 1fr 1fr 2fr auto" }}>
              <span className="font-semibold text-foreground">{item.action}</span>
              <span className="text-muted-foreground">{item.user}</span>
              <span className="font-mono text-muted-foreground text-[10.5px]">{item.date}</span>
              <span className="font-mono text-[10.5px]" style={{ color: CB }}>{item.hash}</span>
              <CheckCircle size={12} style={{ color: OK }} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function RoleWorkspace() {
  const [role, setRole] = useState("compliance");
  return (
    <div className="flex flex-col h-full overflow-auto">
      <PageHeader title="Role Workspace" sub="Adaptive dashboard views based on user role">
        <div className="flex gap-1 p-1 rounded-lg border border-border bg-secondary/40">
          {ROLES.map(({ id, label, Icon }) => {
            const on = role === id;
            return (
              <button key={id} onClick={() => setRole(id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-[11.5px] font-semibold transition-all ${
                  on ? "text-white shadow-sm" : "text-muted-foreground hover:text-foreground"
                }`}
                style={on ? { background: CB } : {}}>
                <Icon size={11} />
                {label}
              </button>
            );
          })}
        </div>
      </PageHeader>
      <div className="flex-1 p-6">
        {role === "compliance" && <ComplianceOfficerView />}
        {role === "it"         && <ITTeamView />}
        {role === "cxo"        && <CXOView />}
        {role === "auditor"    && <AuditorView />}
      </div>
    </div>
  );
}

/* ─── SECURITY PAGE ─────────────────────────────────────────────────────── */

const SEC_FEATURES = [
  { Icon: Database,    title: "Zero Data Retention",      badge: "Privacy-First", desc: "No customer PII is stored or processed. Only cryptographic hashes of compliance evidence are written to the immutable blockchain ledger." },
  { Icon: Building2,   title: "Multi-Tenancy",            badge: "Isolated",      desc: "Full tenant isolation via Hyperledger Fabric channels. Each bank's data is cryptographically separated — no cross-contamination possible." },
  { Icon: Fingerprint, title: "RBAC Access Control",      badge: "Zero Trust",    desc: "Role-Based Access Control enforced at every API layer. Compliance Officer, IT Team, CXO, and RBI Auditor roles have distinct permissions." },
  { Icon: Hash,        title: "Hash-Only Storage",        badge: "Immutable",     desc: "Documents are never stored on-chain. Only SHA-256 hashes with X.509 digital signatures are recorded in the tamper-proof ledger." },
  { Icon: Lock,        title: "End-to-End Encryption",   badge: "TLS 1.3",       desc: "All API communications use TLS 1.3. Fabric peer communications use mutual TLS. Keys managed via HSM-backed infrastructure." },
  { Icon: Globe,       title: "Regulatory Compliance",   badge: "Certified",     desc: "Designed to meet RBI IT Framework, SEBI Cybersecurity Guidelines, ISO 27001, and SOC 2 Type II standards." },
];

function SecurityPage() {
  return (
    <div className="flex flex-col h-full overflow-auto">
      <PageHeader title="Security & Trust" sub="Enterprise-grade security architecture · ISO 27001 · SOC 2 Type II" />
      <div className="p-6 space-y-5">
        {/* Banner */}
        <div className="rounded-xl p-6 relative overflow-hidden" style={{ background: CB }}>
          <div className="absolute inset-0 opacity-[0.07]"
            style={{ backgroundImage: "repeating-linear-gradient(45deg, transparent, transparent 18px, rgba(255,255,255,1) 18px, rgba(255,255,255,1) 36px)" }} />
          <div className="relative flex items-center justify-between gap-6">
            <div>
              <h2 className="text-[20px] font-extrabold text-white mb-1.5" style={{ fontFamily: "Barlow, sans-serif" }}>
                Trust, Verified by Design
              </h2>
              <p className="text-[12.5px] text-white/70 max-w-lg leading-relaxed" style={{ fontFamily: "Inter" }}>
                ARC Shield is built on Hyperledger Fabric with cryptographic proofs, ensuring regulatory evidence is tamper-proof, verifiable, and completely auditable by the RBI at any time.
              </p>
            </div>
            <div className="flex items-center gap-4 shrink-0">
              {["ISO 27001", "SOC 2 II", "RBI IT", "SEBI Cyber"].map(cert => (
                <div key={cert} className="flex flex-col items-center gap-1">
                  <div className="w-14 h-14 rounded-full border-2 border-white/30 flex items-center justify-center">
                    <span className="text-[8.5px] font-extrabold text-white text-center leading-tight">{cert}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Feature grid */}
        <div className="grid grid-cols-3 gap-4">
          {SEC_FEATURES.map((f, i) => (
            <div key={i} className="bg-white border border-border rounded-lg p-5 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ background: `${CB}11` }}>
                  <f.Icon size={17} style={{ color: CB }} />
                </div>
                <span className="text-[9.5px] font-extrabold px-2 py-0.5 rounded"
                  style={{ background: `${CY}25`, color: "#7a5200" }}>
                  {f.badge}
                </span>
              </div>
              <h3 className="text-[13px] font-bold text-foreground mb-2" style={{ fontFamily: "Barlow, sans-serif" }}>{f.title}</h3>
              <p className="text-[11.5px] text-muted-foreground leading-relaxed" style={{ fontFamily: "Inter" }}>{f.desc}</p>
            </div>
          ))}
        </div>

        {/* Metrics row */}
        <div className="bg-white border border-border rounded-lg p-5">
          <h3 className="text-sm font-bold mb-4" style={{ fontFamily: "Barlow", color: "#0a1628" }}>Security Posture Metrics</h3>
          <div className="grid grid-cols-5 gap-4">
            {[
              { label: "Open Vulnerabilities",   value: "0",      color: OK },
              { label: "Pen Tests / Year",        value: "4",      color: CB },
              { label: "Data Breaches",           value: "0",      color: OK },
              { label: "Platform Uptime",         value: "99.95%", color: CB },
              { label: "Audit Log Retention",     value: "7 Yrs",  color: CB },
            ].map((m, i) => (
              <div key={i} className="text-center p-4 rounded-lg border border-border">
                <div className="text-[26px] font-extrabold" style={{ fontFamily: "Barlow", color: m.color }}>{m.value}</div>
                <div className="text-[10px] text-muted-foreground mt-1">{m.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

/* ─── APP ROOT ──────────────────────────────────────────────────────────── */

export default function App() {
  const [active, setActive] = useState("dashboard");
  return (
    <div className="flex h-screen overflow-hidden bg-background" style={{ fontFamily: "Inter, sans-serif" }}>
      <Sidebar active={active} setActive={setActive} />
      <main className="flex-1 overflow-hidden flex flex-col">
        {active === "dashboard"  && <ExecutiveDashboard />}
        {active === "circular"   && <CircularExplorer />}
        {active === "copilot"    && <ComplianceCopilot />}
        {active === "blockchain" && <BlockchainTrustCenter />}
        {active === "roles"      && <RoleWorkspace />}
        {active === "security"   && <SecurityPage />}
      </main>
    </div>
  );
}
