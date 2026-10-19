import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import type { Classification } from '@/types';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function classificationColor(c: Classification | string): string {
  const map: Record<string, string> = {
    safe: '#34d399',
    suspicious: '#fbbf24',
    phishing: '#f87171',
  };
  return map[c] || '#a1a1aa';
}

export function classificationBg(c: Classification | string): string {
  const map: Record<string, string> = {
    safe: 'risk-badge-safe',
    suspicious: 'risk-badge-suspicious',
    phishing: 'risk-badge-phishing',
  };
  return map[c] || '';
}

export function formatDate(iso: string): string {
  if (!iso) return '';
  return new Date(iso).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit',
  });
}

export function riskLabel(score: number): string {
  if (score >= 75) return 'Critical';
  if (score >= 50) return 'High';
  if (score >= 25) return 'Medium';
  return 'Low';
}

/** Shared Recharts styling — consistent across all chart containers */
export const chartTheme = {
  colors: { safe: '#34d399', suspicious: '#fbbf24', phishing: '#f87171', accent: '#2dd4bf' },
  axis: { fill: '#71717a', fontSize: 11 },
  grid: { stroke: 'rgba(255,255,255,0.04)', strokeDasharray: '3 3' },
  tooltip: {
    background: '#151a23',
    border: '1px solid rgba(255,255,255,0.08)',
    borderRadius: 8,
    color: '#f4f4f5',
    fontSize: 12,
    padding: '8px 12px',
  },
} as const;
