import type { LucideIcon } from 'lucide-react';
import type { ReactNode } from 'react';

interface SectionCardProps {
  title: string;
  icon?: LucideIcon;
  children: ReactNode;
  className?: string;
  action?: ReactNode;
}

export default function SectionCard({ title, icon: Icon, children, className = '', action }: SectionCardProps) {
  return (
    <div className={`surface overflow-hidden ${className}`}>
      <div className="card-header">
        <h3 className="text-sm font-medium text-[var(--color-text)] flex items-center gap-2.5">
          {Icon && <Icon className="w-4 h-4 text-[var(--color-text-muted)] opacity-80" strokeWidth={1.75} />}
          {title}
        </h3>
        {action}
      </div>
      <div className="card-body">{children}</div>
    </div>
  );
}
