import { classificationBg } from '@/lib/utils';

interface ClassificationBadgeProps {
  classification: string;
  size?: 'sm' | 'md' | 'lg';
}

export default function ClassificationBadge({ classification, size = 'md' }: ClassificationBadgeProps) {
  const sizes = {
    sm: 'h-[20px] px-2 text-[10px]',
    md: 'h-[22px] px-2.5 text-[11px]',
    lg: 'h-[26px] px-3 text-xs',
  };

  return (
    <span className={`risk-badge ${classificationBg(classification)} ${sizes[size]}`}>
      {classification}
    </span>
  );
}
