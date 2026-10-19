import type { LucideIcon } from 'lucide-react';

interface StatCardProps {
  icon: LucideIcon;
  label: string;
  value: string | number;
  variant?: 'info' | 'safe' | 'warn' | 'danger';
  subtext?: string;
}

export default function StatCard({ icon: Icon, label, value, variant = 'info', subtext }: StatCardProps) {
  const accent = {
    info: 'metric-info',
    safe: 'metric-safe',
    warn: 'metric-warn',
    danger: 'metric-danger',
  }[variant];

  return (
    <div className={`surface metric-card h-full ${accent}`}>
      <div className="flex items-start justify-between gap-3">
        <p className="label-xs">{label}</p>
        <Icon className="w-4 h-4 text-[var(--color-text-muted)] shrink-0 opacity-70" strokeWidth={1.75} />
      </div>
      <div className="mt-auto pt-4">
        <p className="metric-value tabular-nums">{value}</p>
        {subtext && <p className="text-xs text-[var(--color-text-muted)] mt-2">{subtext}</p>}
      </div>
    </div>
  );
}
