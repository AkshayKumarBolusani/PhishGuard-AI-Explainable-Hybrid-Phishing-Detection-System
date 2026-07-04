import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Shield, ShieldAlert, ShieldCheck, ShieldX, TrendingUp, BarChart3,
  ArrowRight, Scan, Activity,
} from 'lucide-react';
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
  PieChart, Pie, Cell, BarChart, Bar,
} from 'recharts';
import { dashboardAPI, historyAPI } from '@/services/api';
import PageHeader from '@/components/ui/PageHeader';
import StatCard from '@/components/ui/StatCard';
import EmptyState from '@/components/ui/EmptyState';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import ClassificationBadge from '@/components/ui/ClassificationBadge';
import type { DashboardStats, ThreatTrend, AttackTypeCount, ScanListItem } from '@/types';
import { chartTheme, classificationColor, formatDate } from '@/lib/utils';

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [trends, setTrends] = useState<ThreatTrend[]>([]);
  const [attackTypes, setAttackTypes] = useState<AttackTypeCount[]>([]);
  const [recentScans, setRecentScans] = useState<ScanListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      dashboardAPI.getStatistics(),
      dashboardAPI.getTrends(30),
      dashboardAPI.getAttackTypes(),
      historyAPI.getHistory({ page: 1, page_size: 5 }),
    ])
      .then(([s, t, a, h]) => {
        setStats(s.data.data);
        setTrends(t.data.data);
        setAttackTypes(a.data.data);
        setRecentScans(h.data.data.items);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner label="Loading dashboard..." />;

  const hasData = (stats?.total_scans || 0) > 0;
  const pieData = [
    { name: 'Safe', value: stats?.safe_count || 0, color: chartTheme.colors.safe },
    { name: 'Suspicious', value: stats?.suspicious_count || 0, color: chartTheme.colors.suspicious },
    { name: 'Phishing', value: stats?.phishing_count || 0, color: chartTheme.colors.phishing },
  ];
  const detectionRate = stats && stats.total_scans > 0
    ? (((stats.suspicious_count + stats.phishing_count) / stats.total_scans) * 100).toFixed(1)
    : '0.0';

  return (
    <div className="page-stack">
      <PageHeader
        title="Threat overview"
        subtitle="Scan volume, classification breakdown, and recent detections"
        actions={
          <Link to="/scanner" className="btn-accent">
            <Scan className="w-4 h-4" strokeWidth={2} />
            New scan
          </Link>
        }
      />

      <div className="grid grid-cols-2 xl:grid-cols-4 grid-gap-lg">
        <StatCard icon={Shield} label="Total scans" value={stats?.total_scans ?? 0} variant="info" />
        <StatCard icon={ShieldCheck} label="Safe" value={stats?.safe_count ?? 0} variant="safe" />
        <StatCard icon={ShieldAlert} label="Suspicious" value={stats?.suspicious_count ?? 0} variant="warn" />
        <StatCard icon={ShieldX} label="Phishing" value={stats?.phishing_count ?? 0} variant="danger" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 grid-gap-lg">
        <div className="surface xl:col-span-2 overflow-hidden">
          <div className="card-header">
            <div className="flex items-center gap-2.5">
              <TrendingUp className="w-4 h-4 text-[var(--color-text-muted)]" strokeWidth={1.75} />
              <h3 className="text-sm font-medium text-[var(--color-text)]">Threat trends</h3>
            </div>
            <span className="text-xs text-[var(--color-text-muted)]">Last 30 days</span>
          </div>
          <div className="card-body-lg pt-4">
            {hasData ? (
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={trends} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
                  <defs>
                    <linearGradient id="sg" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor={chartTheme.colors.safe} stopOpacity={0.2} /><stop offset="95%" stopColor={chartTheme.colors.safe} stopOpacity={0} /></linearGradient>
                    <linearGradient id="ug" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor={chartTheme.colors.suspicious} stopOpacity={0.2} /><stop offset="95%" stopColor={chartTheme.colors.suspicious} stopOpacity={0} /></linearGradient>
                    <linearGradient id="pg" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor={chartTheme.colors.phishing} stopOpacity={0.2} /><stop offset="95%" stopColor={chartTheme.colors.phishing} stopOpacity={0} /></linearGradient>
                  </defs>
                  <CartesianGrid {...chartTheme.grid} vertical={false} />
                  <XAxis dataKey="date" tick={chartTheme.axis} axisLine={false} tickLine={false} tickFormatter={(v) => new Date(v).toLocaleDateString('en', { month: 'short', day: 'numeric' })} dy={8} />
                  <YAxis tick={chartTheme.axis} axisLine={false} tickLine={false} allowDecimals={false} dx={-4} />
                  <Tooltip contentStyle={chartTheme.tooltip} cursor={{ stroke: 'rgba(255,255,255,0.08)' }} />
                  <Area type="monotone" dataKey="safe" stroke={chartTheme.colors.safe} fill="url(#sg)" strokeWidth={1.5} name="Safe" />
                  <Area type="monotone" dataKey="suspicious" stroke={chartTheme.colors.suspicious} fill="url(#ug)" strokeWidth={1.5} name="Suspicious" />
                  <Area type="monotone" dataKey="phishing" stroke={chartTheme.colors.phishing} fill="url(#pg)" strokeWidth={1.5} name="Phishing" />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <EmptyState
                icon={Activity}
                title="No scan data yet"
                description="Run your first email scan to populate threat trends."
                actionLabel="Scan an email"
                actionTo="/scanner"
              />
            )}
          </div>
        </div>

        <div className="surface overflow-hidden">
          <div className="card-header">
            <div className="flex items-center gap-2.5">
              <BarChart3 className="w-4 h-4 text-[var(--color-text-muted)]" strokeWidth={1.75} />
              <h3 className="text-sm font-medium text-[var(--color-text)]">Classification</h3>
            </div>
          </div>
          <div className="card-body-lg">
            {hasData ? (
              <>
                <ResponsiveContainer width="100%" height={192}>
                  <PieChart>
                    <Pie data={pieData.filter((d) => d.value > 0)} cx="50%" cy="50%" innerRadius={52} outerRadius={76} paddingAngle={2} dataKey="value" strokeWidth={0}>
                      {pieData.filter((d) => d.value > 0).map((entry, i) => (
                        <Cell key={i} fill={entry.color} />
                      ))}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
                <div className="space-y-3 mt-4 pt-4 border-t border-[var(--color-border-subtle)]">
                  {pieData.map((d) => (
                    <div key={d.name} className="flex items-center justify-between">
                      <div className="flex items-center gap-2.5">
                        <div className="w-2 h-2 rounded-full shrink-0" style={{ background: d.color }} />
                        <span className="text-sm text-[var(--color-text-secondary)]">{d.name}</span>
                      </div>
                      <span className="text-sm font-semibold text-[var(--color-text)] tabular-nums">{d.value}</span>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <p className="text-sm text-[var(--color-text-muted)] text-center py-20">Charts appear after your first scan</p>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 grid-gap-lg">
        {[
          { label: 'Avg. risk score', value: stats?.average_risk_score?.toFixed(1) ?? '0.0' },
          { label: 'Scans today', value: String(stats?.daily_scans ?? 0) },
          { label: 'This week', value: String(stats?.weekly_scans ?? 0) },
          { label: 'Detection rate', value: `${detectionRate}%` },
        ].map((item) => (
          <div key={item.label} className="surface metric-card">
            <p className="label-xs">{item.label}</p>
            <p className="metric-value tabular-nums mt-auto pt-4">{item.value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 grid-gap-lg">
        <div className="surface overflow-hidden">
          <div className="card-header">
            <h3 className="text-sm font-medium text-[var(--color-text)]">Recent scans</h3>
            <Link to="/history" className="text-xs font-medium text-[var(--color-accent)] hover:text-[var(--color-accent-hover)] flex items-center gap-1 transition-colors">
              View all <ArrowRight className="w-3 h-3" strokeWidth={2} />
            </Link>
          </div>
          <div className="card-body pt-2">
            {recentScans.length > 0 ? (
              <div>
                {recentScans.map((scan, i) => (
                  <Link
                    key={scan.id}
                    to={`/report/${scan.id}`}
                    className={`flex items-center gap-4 py-4 transition-colors hover:bg-white/[0.02] -mx-5 px-5 ${i !== recentScans.length - 1 ? 'border-b border-[var(--color-border-subtle)]' : ''}`}
                  >
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-[var(--color-text)] truncate">{scan.subject}</p>
                      <p className="text-xs text-[var(--color-text-muted)] mono truncate mt-1">{scan.sender}</p>
                    </div>
                    <ClassificationBadge classification={scan.classification} size="sm" />
                    <span
                      className="text-sm font-semibold tabular-nums shrink-0 hidden sm:block w-10 text-right"
                      style={{ color: classificationColor(scan.classification) }}
                    >
                      {scan.risk_score.toFixed(0)}
                    </span>
                    <span className="text-xs text-[var(--color-text-muted)] shrink-0 hidden md:block w-28 text-right">{formatDate(scan.created_at)}</span>
                  </Link>
                ))}
              </div>
            ) : (
              <p className="text-sm text-[var(--color-text-muted)] text-center py-12">No scans yet</p>
            )}
          </div>
        </div>

        <div className="surface overflow-hidden">
          <div className="card-header">
            <h3 className="text-sm font-medium text-[var(--color-text)]">Top attack categories</h3>
          </div>
          <div className="card-body-lg pt-2">
            {attackTypes.length > 0 ? (
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={attackTypes.slice(0, 6)} layout="vertical" margin={{ left: 4, right: 16, top: 4, bottom: 4 }}>
                  <CartesianGrid {...chartTheme.grid} horizontal={false} />
                  <XAxis type="number" tick={chartTheme.axis} axisLine={false} tickLine={false} allowDecimals={false} />
                  <YAxis type="category" dataKey="attack_type" tick={{ ...chartTheme.axis, fill: '#a1a1aa' }} axisLine={false} tickLine={false} width={104} tickFormatter={(v) => v.replace(/_/g, ' ')} />
                  <Tooltip contentStyle={chartTheme.tooltip} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
                  <Bar dataKey="count" fill={chartTheme.colors.accent} radius={[0, 4, 4, 0]} barSize={14} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-sm text-[var(--color-text-muted)] text-center py-12">Attack patterns will appear here</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
