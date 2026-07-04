import { motion } from 'framer-motion';
import ClassificationBadge from './ClassificationBadge';
import { classificationColor } from '@/lib/utils';

interface RiskGaugeProps {
  score: number;
  classification: string;
  confidence: number;
}

export default function RiskGauge({ score, classification, confidence }: RiskGaugeProps) {
  const color = classificationColor(classification);
  const circumference = 2 * Math.PI * 46;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="flex items-center gap-8">
      <div className="relative w-[120px] h-[120px] shrink-0">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120" aria-hidden>
          <circle cx="60" cy="60" r="46" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="5" />
          <motion.circle
            cx="60" cy="60" r="46" fill="none" stroke={color} strokeWidth="5" strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 0.6, ease: [0.4, 0, 0.2, 1] }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-semibold text-[var(--color-text)] tabular-nums tracking-tight">{score.toFixed(0)}</span>
          <span className="label-xs mt-1">Risk score</span>
        </div>
      </div>
      <div className="flex-1 min-w-0 space-y-4">
        <ClassificationBadge classification={classification} size="md" />
        <div>
          <p className="label-xs mb-1.5">Confidence</p>
          <p className="text-3xl font-semibold tabular-nums tracking-tight" style={{ color }}>{(confidence * 100).toFixed(1)}%</p>
        </div>
      </div>
    </div>
  );
}
