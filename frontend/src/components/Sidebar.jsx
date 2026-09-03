import {
  Brain,
  FileText,
  History,
  LayoutDashboard,
  MessageSquarePlus,
  Settings,
} from 'lucide-react'
import { NavLink } from 'react-router-dom'
import { useHealth } from '../hooks/useHealth'

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/chat', label: 'New Chat', icon: MessageSquarePlus },
  { to: '/documents', label: 'Documents', icon: FileText },
  { to: '/conversations', label: 'Conversations', icon: History },
  { to: '/settings', label: 'Settings', icon: Settings },
]

export function Sidebar() {
  const { online } = useHealth()

  return (
    <aside className="flex h-full w-60 shrink-0 flex-col bg-sidebar text-white">
      <div className="flex items-center gap-2 px-5 py-6">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-accent">
          <Brain size={17} />
        </div>
        <div>
          <p className="text-sm font-semibold leading-tight">EvidenceRAG</p>
          <p className="text-xs text-white/50">Evidence-Based AI</p>
        </div>
      </div>

      <nav className="flex-1 space-y-1 px-3">
        {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-accent text-white'
                  : 'text-white/70 hover:bg-sidebar-hover hover:text-white'
              }`
            }
          >
            <Icon size={17} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-sidebar-border px-5 py-4">
        <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-white/40">
          System Status
        </p>
        <div className="flex items-center gap-2 text-sm">
          <span
            className={`h-2 w-2 rounded-full ${
              online === null ? 'bg-white/30' : online ? 'bg-success' : 'bg-danger'
            }`}
            aria-hidden="true"
          />
          <span className="text-white/80">
            Backend {online === null ? 'Checking...' : online ? 'Online' : 'Offline'}
          </span>
        </div>
      </div>
    </aside>
  )
}
