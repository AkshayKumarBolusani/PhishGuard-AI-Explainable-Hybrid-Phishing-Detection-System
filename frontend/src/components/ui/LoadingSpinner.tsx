interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  label?: string;
}

export default function LoadingSpinner({ size = 'md', label }: LoadingSpinnerProps) {
  const sizes = { sm: 'w-5 h-5 border-2', md: 'w-8 h-8 border-2', lg: 'w-10 h-10 border-[3px]' };

  return (
    <div className="flex flex-col items-center justify-center gap-4 py-16" role="status" aria-live="polite">
      <div className={`${sizes[size]} border-white/8 border-t-[var(--color-accent)] rounded-full animate-spin-slow`} />
      {label && <p className="text-sm text-[var(--color-text-secondary)]">{label}</p>}
    </div>
  );
}
