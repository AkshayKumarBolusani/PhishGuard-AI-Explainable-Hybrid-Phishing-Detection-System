import { useState } from 'react';
import {
  Scan, Shield, AlertTriangle, Link2, User, Brain, FileText, Loader2,
  ChevronRight,
} from 'lucide-react';
import { scanAPI } from '@/services/api';
import { useScanStore } from '@/store';
import { classificationColor } from '@/lib/utils';
import PageHeader from '@/components/ui/PageHeader';
import RiskGauge from '@/components/ui/RiskGauge';
import SectionCard from '@/components/ui/SectionCard';
import ClassificationBadge from '@/components/ui/ClassificationBadge';
import type { ScanResult } from '@/types';

const EXAMPLE = {
  subject: 'Urgent: Your PayPal account has been compromised',
  sender: 'security@paypa1-support.tk',
  receiver: 'user@example.com',
  body: `Dear valued customer,

We have detected unauthorized activity on your PayPal account. Your account has been temporarily limited.

To restore access, you must verify your identity immediately by clicking the link below:

http://paypa1-secure-verify.tk/account/restore?id=8827361

If you do not verify within 24 hours, your account will be permanently suspended and all funds will be frozen.

Please also confirm your Social Security Number and date of birth for identity verification.

Thank you,
PayPal Security Team`,
};

function severityClass(severity: string) {
  const map: Record<string, string> = {
    critical: 'severity-critical',
    high: 'severity-high',
    medium: 'severity-medium',
    low: 'severity-low',
  };
  return map[severity] || 'severity-low';
}

export default function ScannerPage() {
  const [form, setForm] = useState({ subject: '', sender: '', receiver: '', body: '' });
  const [activeTab, setActiveTab] = useState<'overview' | 'indicators' | 'models'>('overview');
  const { currentScan, isScanning, setCurrentScan, setIsScanning } = useScanStore();

  const handleScan = async () => {
    if (!form.subject.trim() || !form.sender.trim() || !form.body.trim()) return;
    setIsScanning(true);
    setCurrentScan(null);
    try {
      const res = await scanAPI.scan(form);
      setCurrentScan(res.data.data);
      setActiveTab('overview');
    } catch (err) {
      console.error('Scan failed:', err);
    } finally {
      setIsScanning(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] md:h-[calc(100vh-6rem)] -mx-5 -mt-6 md:-mx-8 md:-mt-8">
      <div className="px-5 md:px-8 pt-6 md:pt-8 pb-5 border-b border-[var(--color-border-subtle)] bg-[var(--color-bg)]">
        <PageHeader
          title="Email scanner"
          subtitle="Hybrid pipeline: rules, ML, NLP, and LLM explainability"
          actions={
            <button type="button" onClick={() => setForm(EXAMPLE)} className="btn-ghost">
              Load example
            </button>
          }
          className="mb-0"
        />
      </div>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 min-h-0">
        {/* Input panel */}
        <div className="flex flex-col border-b lg:border-b-0 lg:border-r border-[var(--color-border-subtle)] bg-[var(--color-surface)]">
          <div className="px-5 py-4 border-b border-[var(--color-border-subtle)]">
            <span className="label-xs">Email input</span>
          </div>
          <div className="flex-1 overflow-y-auto px-5 py-5 space-y-5">
            <div>
              <label htmlFor="scan-subject" className="label-xs mb-2 block">Subject</label>
              <input id="scan-subject" value={form.subject} onChange={(e) => setForm({ ...form, subject: e.target.value })} className="field" placeholder="Email subject line" />
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label htmlFor="scan-sender" className="label-xs mb-2 block">Sender</label>
                <input id="scan-sender" value={form.sender} onChange={(e) => setForm({ ...form, sender: e.target.value })} className="field mono text-[13px]" placeholder="sender@email.com" />
              </div>
              <div>
                <label htmlFor="scan-receiver" className="label-xs mb-2 block">Receiver</label>
                <input id="scan-receiver" value={form.receiver} onChange={(e) => setForm({ ...form, receiver: e.target.value })} className="field mono text-[13px]" placeholder="receiver@email.com" />
              </div>
            </div>
            <div>
              <label htmlFor="scan-body" className="label-xs mb-2 block">Body</label>
              <textarea
                id="scan-body"
                value={form.body}
                onChange={(e) => setForm({ ...form, body: e.target.value })}
                className="field resize-none mono text-[13px] leading-relaxed min-h-[300px] lg:min-h-[380px]"
                placeholder="Paste the full email body..."
              />
            </div>
          </div>
          <div className="px-5 py-5 border-t border-[var(--color-border-subtle)]">
            <button
              type="button"
              onClick={handleScan}
              disabled={isScanning || !form.subject || !form.sender || !form.body}
              className="btn-accent w-full h-10"
            >
              {isScanning ? (
                <><Loader2 className="w-4 h-4 animate-spin-slow" strokeWidth={2} />Analyzing...</>
              ) : (
                <><Scan className="w-4 h-4" strokeWidth={2} />Analyze email</>
              )}
            </button>
          </div>
        </div>

        {/* Results panel */}
        <div className="flex flex-col min-h-0 bg-[var(--color-bg)]">
          <div className="px-5 py-4 border-b border-[var(--color-border-subtle)]">
            <span className="label-xs">Analysis output</span>
          </div>
          <div className="flex-1 overflow-y-auto px-5 py-5">
            {isScanning ? (
              <div className="flex flex-col items-center justify-center h-full min-h-[360px]">
                <div className="w-9 h-9 border-2 border-white/8 border-t-[var(--color-accent)] rounded-full animate-spin-slow mb-5" />
                <p className="text-sm font-medium text-[var(--color-text)]">Running analysis</p>
                <p className="text-xs text-[var(--color-text-muted)] mt-2">Rules → ML → NLP → Report</p>
              </div>
            ) : currentScan ? (
              <ScanResults scan={currentScan} activeTab={activeTab} setActiveTab={setActiveTab} />
            ) : (
              <div className="flex flex-col items-center justify-center h-full min-h-[360px] text-center px-6">
                <div className="w-12 h-12 rounded-[var(--radius-lg)] bg-[var(--color-surface)] border border-[var(--color-border-subtle)] flex items-center justify-center mb-5">
                  <Shield className="w-5 h-5 text-[var(--color-text-muted)]" strokeWidth={1.75} />
                </div>
                <p className="text-sm font-medium text-[var(--color-text)]">No analysis yet</p>
                <p className="text-body mt-2 max-w-xs">
                  Enter email details or load the example to see indicators, URL checks, and model comparison.
                </p>
                <button type="button" onClick={() => setForm(EXAMPLE)} className="btn-ghost mt-6">
                  Try example email
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function ScanResults({ scan, activeTab, setActiveTab }: { scan: ScanResult; activeTab: string; setActiveTab: (t: 'overview' | 'indicators' | 'models') => void }) {
  const tabs = [
    { id: 'overview' as const, label: 'Overview' },
    { id: 'indicators' as const, label: `Indicators (${scan.indicators.length})` },
    { id: 'models' as const, label: 'Models' },
  ];

  return (
    <div className="section-stack">
      <div className="surface card-body-lg" style={{ borderLeft: `3px solid ${classificationColor(scan.classification)}` }}>
        <RiskGauge score={scan.risk_score} classification={scan.classification} confidence={scan.confidence} />
        <div className="mt-8 pt-6 border-t border-[var(--color-border-subtle)] space-y-3">
          {Object.entries(scan.probabilities).map(([label, prob]) => (
            <div key={label} className="flex items-center gap-4">
              <span className="text-xs text-[var(--color-text-muted)] w-20 capitalize shrink-0">{label}</span>
              <div className="flex-1 h-1.5 bg-white/[0.05] rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{ width: `${(prob as number) * 100}%`, background: classificationColor(label) }}
                />
              </div>
              <span className="text-xs font-medium text-[var(--color-text-secondary)] w-12 text-right tabular-nums shrink-0">{((prob as number) * 100).toFixed(1)}%</span>
            </div>
          ))}
        </div>
        <p className="text-xs text-[var(--color-text-muted)] mt-5 mono tabular-nums">{scan.processing_time_ms.toFixed(0)}ms processing time</p>
      </div>

      <div className="flex flex-wrap gap-2">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id)}
            className={`chip ${activeTab === tab.id ? 'chip-active' : ''}`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'overview' && (
        <div className="section-stack">
          <SectionCard title="AI explanation" icon={Brain}>
            <p className="text-body">{scan.explanation}</p>
          </SectionCard>

          {scan.urls_analysis.length > 0 && (
            <SectionCard title={`URLs (${scan.urls_analysis.length})`} icon={Link2}>
              <div className="space-y-3">
                {scan.urls_analysis.map((url, i) => (
                  <div key={i} className="surface-elevated p-4">
                    <p className="text-xs text-[var(--color-text-secondary)] mono break-all leading-relaxed">{url.original_url}</p>
                    <div className="flex flex-wrap gap-2 mt-3">
                      <span className="text-[11px] px-2 py-0.5 rounded-[var(--radius-sm)] bg-white/[0.04] text-[var(--color-text-muted)]">{url.domain}</span>
                      {!url.is_https && <span className="text-[11px] px-2 py-0.5 rounded-[var(--radius-sm)] severity-high">No HTTPS</span>}
                      {url.is_homograph && <span className="text-[11px] px-2 py-0.5 rounded-[var(--radius-sm)] severity-critical">Typosquat</span>}
                      <span className="text-[11px] px-2 py-0.5 rounded-[var(--radius-sm)] bg-white/[0.04] text-[var(--color-text-muted)] tabular-nums">Risk {(url.suspicious_score * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </SectionCard>
          )}

          <SectionCard title="Sender analysis" icon={User}>
            <div className="grid grid-cols-2 gap-4">
              <div className="surface-elevated p-4">
                <span className="label-xs block mb-2">Domain</span>
                <span className="text-sm text-[var(--color-text)]">{scan.sender_analysis.domain}</span>
              </div>
              <div className="surface-elevated p-4">
                <span className="label-xs block mb-2">Trust score</span>
                <span className="text-xl font-semibold tabular-nums" style={{ color: scan.sender_analysis.trust_score > 60 ? '#34d399' : '#f87171' }}>{scan.sender_analysis.trust_score}%</span>
              </div>
            </div>
            {scan.sender_analysis.is_typosquatting && (
              <p className="text-xs mt-4 p-4 rounded-[var(--radius-md)] severity-critical leading-relaxed">
                Typosquatting detected — impersonates {scan.sender_analysis.spoofed_domain}
              </p>
            )}
          </SectionCard>

          <SectionCard title="Security report" icon={Shield}>
            <p className="text-body">{scan.security_report.executive_summary}</p>
            {scan.security_report.recommended_actions?.length > 0 && (
              <ul className="mt-5 space-y-2">
                {scan.security_report.recommended_actions.map((action, i) => (
                  <li key={i} className="text-sm text-[var(--color-text-secondary)] flex gap-2.5 leading-relaxed">
                    <ChevronRight className="w-3.5 h-3.5 text-[var(--color-accent)] shrink-0 mt-0.5" strokeWidth={2} />
                    {action}
                  </li>
                ))}
              </ul>
            )}
          </SectionCard>
        </div>
      )}

      {activeTab === 'indicators' && (
        <SectionCard title={`Threat indicators (${scan.indicators.length})`} icon={AlertTriangle}>
          <div className="space-y-3 max-h-[520px] overflow-y-auto pr-1">
            {scan.indicators.map((ind, i) => (
              <div key={i} className="flex gap-4 p-4 surface-elevated">
                <span className={`text-[10px] px-2 py-1 rounded-[var(--radius-sm)] font-semibold uppercase shrink-0 h-fit ${severityClass(ind.severity)}`}>{ind.severity}</span>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-[var(--color-text)] leading-snug">{ind.description}</p>
                  {ind.matched_text && (
                    <p className="text-xs text-[var(--color-accent)] mt-2 mono bg-[var(--color-accent-dim)] px-2.5 py-1.5 rounded-[var(--radius-sm)] truncate">
                      "{ind.matched_text}"
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </SectionCard>
      )}

      {activeTab === 'models' && scan.model_results.length > 0 && (
        <SectionCard title="Model comparison" icon={FileText}>
          <div className="space-y-3">
            {scan.model_results.map((m, i) => (
              <div key={i} className="flex items-center justify-between p-4 surface-elevated">
                <div>
                  <p className="text-sm font-medium text-[var(--color-text)]">{m.model_name}</p>
                  <p className="text-xs text-[var(--color-text-muted)] mt-1 mono tabular-nums">{m.latency_ms.toFixed(1)}ms</p>
                </div>
                <div className="flex items-center gap-3">
                  <ClassificationBadge classification={m.classification} size="sm" />
                  <span className="text-sm font-semibold text-[var(--color-text)] tabular-nums w-14 text-right">{(m.confidence * 100).toFixed(1)}%</span>
                </div>
              </div>
            ))}
          </div>
        </SectionCard>
      )}
    </div>
  );
}
