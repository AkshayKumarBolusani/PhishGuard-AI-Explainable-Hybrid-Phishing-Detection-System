import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Shield, AlertTriangle, Brain, ChevronRight } from 'lucide-react';
import { scanAPI } from '@/services/api';
import PageHeader from '@/components/ui/PageHeader';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import ClassificationBadge from '@/components/ui/ClassificationBadge';
import RiskGauge from '@/components/ui/RiskGauge';
import SectionCard from '@/components/ui/SectionCard';
import { classificationColor } from '@/lib/utils';
import type { ScanResult } from '@/types';

export default function ReportPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [scan, setScan] = useState<ScanResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    scanAPI.getScan(id).then((res) => setScan(res.data.data)).catch(console.error).finally(() => setLoading(false));
  }, [id]);

  if (loading) return <LoadingSpinner label="Loading security report..." />;

  if (!scan) {
    return (
      <div className="flex flex-col items-center justify-center py-24">
        <p className="text-body mb-5">Scan not found</p>
        <Link to="/history" className="btn-ghost">← Back to history</Link>
      </div>
    );
  }

  return (
    <div className="page-stack max-w-4xl">
      <div className="flex items-start gap-4">
        <button
          type="button"
          onClick={() => navigate(-1)}
          className="btn-icon border border-[var(--color-border)] mt-1 shrink-0"
          aria-label="Go back"
        >
          <ArrowLeft className="w-4 h-4" strokeWidth={1.75} />
        </button>
        <PageHeader title="Security report" subtitle={`Scan ${scan.id.slice(0, 8)}…`} className="mb-0 flex-1" />
      </div>

      <div
        className="surface card-body-lg"
        style={{ borderLeft: `3px solid ${classificationColor(scan.classification)}` }}
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
          <RiskGauge score={scan.risk_score} classification={scan.classification} confidence={scan.confidence} />
          <div>
            <p className="label-xs mb-3">Executive summary</p>
            <p className="text-body">{scan.security_report?.executive_summary}</p>
            <div className="mt-6 pt-5 border-t border-[var(--color-border-subtle)] flex items-baseline gap-3">
              <span className="label-xs">Security score</span>
              <span className="text-2xl font-semibold tabular-nums tracking-tight" style={{ color: classificationColor(scan.classification) }}>
                {scan.security_report?.security_score || 0}/100
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 grid-gap-lg">
        <SectionCard title="AI explanation" icon={Brain}>
          <p className="text-body">{scan.explanation}</p>
        </SectionCard>
        <SectionCard title="Attack analysis" icon={Shield}>
          <div className="space-y-3">
            <div className="surface-elevated p-4">
              <span className="label-xs block mb-2">Attack type</span>
              <span className="text-sm text-[var(--color-text)] capitalize">{scan.security_report?.attack_type?.replace(/_/g, ' ') || 'Unknown'}</span>
            </div>
            <div className="surface-elevated p-4">
              <span className="label-xs block mb-2">Likely goal</span>
              <span className="text-sm text-[var(--color-text)]">{scan.security_report?.likely_goal || '—'}</span>
            </div>
          </div>
        </SectionCard>
      </div>

      {scan.indicators?.length > 0 && (
        <SectionCard title={`Threat indicators (${scan.indicators.length})`} icon={AlertTriangle}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {scan.indicators.map((ind, i) => (
              <div key={i} className="flex gap-3 p-4 surface-elevated">
                <ClassificationBadge classification={ind.severity === 'critical' || ind.severity === 'high' ? 'phishing' : 'suspicious'} size="sm" />
                <div className="min-w-0 flex-1">
                  <p className="text-sm text-[var(--color-text)] leading-snug">{ind.description}</p>
                  {ind.matched_text && <p className="text-xs text-[var(--color-text-muted)] mt-1.5 truncate mono">"{ind.matched_text}"</p>}
                </div>
              </div>
            ))}
          </div>
        </SectionCard>
      )}

      {scan.security_report?.recommended_actions?.length > 0 && (
        <SectionCard title="Recommended actions" icon={ChevronRight}>
          <ul className="space-y-2">
            {scan.security_report.recommended_actions.map((action, i) => (
              <li key={i} className="flex gap-3 text-sm text-[var(--color-text-secondary)] p-4 surface-elevated leading-relaxed">
                <span className="text-[var(--color-accent)] font-semibold shrink-0 tabular-nums w-5">{i + 1}.</span>
                {action}
              </li>
            ))}
          </ul>
          {scan.security_report.user_advice && (
            <div className="mt-5 p-4 surface-elevated border border-[rgba(45,212,191,0.15)]">
              <p className="label-xs mb-2">User advice</p>
              <p className="text-body">{scan.security_report.user_advice}</p>
            </div>
          )}
        </SectionCard>
      )}
    </div>
  );
}
