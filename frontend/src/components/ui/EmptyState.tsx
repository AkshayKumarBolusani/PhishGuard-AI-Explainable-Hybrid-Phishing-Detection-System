import type { LucideIcon } from 'lucide-react';
import { Link } from 'react-router-dom';

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  actionLabel?: string;
  actionTo?: string;
  onAction?: () => void;
}

export default function EmptyState({ icon: Icon, title, description, actionLabel, actionTo, onAction }: EmptyStateProps) {
  const action = actionLabel && (actionTo ? (
    <Link to={actionTo} className="btn-accent mt-6">{actionLabel}</Link>
  ) : onAction ? (
    <button type="button" onClick={onAction} className="btn-accent mt-6">{actionLabel}</button>
  ) : null);

  return (
    <div className="flex flex-col items-center justify-center py-16 px-8 text-center">
      <div className="w-12 h-12 rounded-[var(--radius-lg)] bg-[var(--color-surface-2)] border border-[var(--color-border-subtle)] flex items-center justify-center mb-5">
        <Icon className="w-5 h-5 text-[var(--color-text-muted)]" strokeWidth={1.75} />
      </div>
      <h3 className="text-sm font-semibold text-[var(--color-text)]">{title}</h3>
      <p className="text-body mt-2 max-w-sm">{description}</p>
      {action}
    </div>
  );
}
