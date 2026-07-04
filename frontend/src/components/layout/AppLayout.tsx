import { useState } from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import { Shield, Scan, LayoutDashboard, History, BarChart3, Settings, Menu, X, ChevronLeft } from 'lucide-react';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/scanner', icon: Scan, label: 'Scanner' },
  { to: '/history', icon: History, label: 'History' },
  { to: '/models', icon: BarChart3, label: 'Models' },
  { to: '/settings', icon: Settings, label: 'Settings' },
];

const pageTitles: Record<string, string> = {
  '/': 'Dashboard',
  '/scanner': 'Email Scanner',
  '/history': 'Scan History',
  '/models': 'Model Analysis',
  '/settings': 'Settings',
};

export default function AppLayout() {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();
  const pageTitle = pageTitles[location.pathname] || 'PhishGuard AI';

  const sidebarContent = (mobile = false) => (
    <>
      <div className={`flex items-center gap-3 px-5 h-16 border-b border-[var(--color-border-subtle)] ${collapsed && !mobile ? 'justify-center px-3' : ''}`}>
        <div className="w-8 h-8 rounded-[var(--radius-md)] bg-[var(--color-accent-dim)] border border-[rgba(45,212,191,0.2)] flex items-center justify-center flex-shrink-0">
          <Shield className="w-4 h-4 text-[var(--color-accent)]" strokeWidth={2} />
        </div>
        {(!collapsed || mobile) && (
          <div className="overflow-hidden flex-1 min-w-0">
            <h1 className="text-sm font-semibold text-[var(--color-text)] tracking-tight truncate">PhishGuard AI</h1>
            <p className="text-[11px] text-[var(--color-text-muted)] mt-0.5">Email threat detection</p>
          </div>
        )}
        {!mobile && (
          <button
            type="button"
            onClick={() => setCollapsed(!collapsed)}
            className="btn-icon shrink-0"
            aria-label="Toggle sidebar"
          >
            <ChevronLeft className={`w-4 h-4 transition-transform duration-[180ms] ${collapsed ? 'rotate-180' : ''}`} strokeWidth={2} />
          </button>
        )}
      </div>

      <nav className="flex-1 py-4">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            onClick={() => mobile && setMobileOpen(false)}
            className={({ isActive }) =>
              `nav-item ${isActive ? 'nav-item-active' : ''} ${collapsed && !mobile ? 'justify-center px-0 mx-3' : ''}`
            }
            title={collapsed && !mobile ? label : undefined}
          >
            <Icon className="w-4 h-4 flex-shrink-0" strokeWidth={1.75} />
            {(!collapsed || mobile) && <span>{label}</span>}
          </NavLink>
        ))}
      </nav>

      {(!collapsed || mobile) && (
        <div className="px-5 py-4 border-t border-[var(--color-border-subtle)]">
          <p className="text-[11px] text-[var(--color-text-muted)]">v1.0 · Hybrid AI pipeline</p>
        </div>
      )}
    </>
  );

  return (
    <div className="flex h-screen overflow-hidden bg-[var(--color-bg)]">
      <aside className={`hidden md:flex flex-col bg-[var(--color-surface)] border-r border-[var(--color-border-subtle)] transition-[width] duration-[180ms] z-20 ${collapsed ? 'w-[72px]' : 'w-[240px]'}`}>
        {sidebarContent()}
      </aside>

      <div className="md:hidden fixed top-0 left-0 right-0 z-50 bg-[var(--color-surface)] border-b border-[var(--color-border-subtle)] h-14 flex items-center px-4">
        <button type="button" onClick={() => setMobileOpen(true)} className="btn-icon -ml-1" aria-label="Open menu">
          <Menu className="w-5 h-5" strokeWidth={1.75} />
        </button>
        <span className="font-semibold text-sm text-[var(--color-text)] mx-auto tracking-tight">{pageTitle}</span>
        <div className="w-8" />
      </div>

      {mobileOpen && (
        <>
          <div className="fixed inset-0 bg-black/50 z-50 md:hidden" onClick={() => setMobileOpen(false)} />
          <aside className="fixed top-0 left-0 bottom-0 w-[240px] bg-[var(--color-surface)] border-r border-[var(--color-border-subtle)] z-50 md:hidden flex flex-col">
            <div className="flex items-center justify-end px-3 h-14 border-b border-[var(--color-border-subtle)]">
              <button type="button" onClick={() => setMobileOpen(false)} className="btn-icon" aria-label="Close menu">
                <X className="w-5 h-5" strokeWidth={1.75} />
              </button>
            </div>
            {sidebarContent(true)}
          </aside>
        </>
      )}

      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <header className="hidden md:flex items-center h-16 px-8 border-b border-[var(--color-border-subtle)] bg-[var(--color-bg)] shrink-0">
          <h2 className="text-sm font-semibold text-[var(--color-text)] tracking-tight">{pageTitle}</h2>
        </header>

        <main className="flex-1 overflow-y-auto">
          <div className="md:hidden h-14" />
          <div className="px-5 py-6 md:px-8 md:py-8 max-w-[1440px] mx-auto w-full">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
