import { useEffect, useState } from 'react';
import { Cpu, Database, Map, Gauge } from 'lucide-react';
import { healthAPI } from '@/services/api';
import PageHeader from '@/components/ui/PageHeader';
import SectionCard from '@/components/ui/SectionCard';
import type { ModelInfo } from '@/types';

const ROADMAP = [
  'Browser extension',
  'Gmail integration',
  'Outlook plugin',
  'VirusTotal integration',
  'Email attachment scanning',
  'OCR for image-based phishing',
  'Multi-language phishing detection',
  'Model retraining pipeline',
  'Kubernetes deployment',
];

function SettingRow({ label, value, ok = true }: { label: string; value: string; ok?: boolean }) {
  return (
    <div className="flex items-center justify-between px-4 py-3.5 surface-elevated min-h-[52px]">
      <span className="text-sm text-[var(--color-text-secondary)]">{label}</span>
      <div className="flex items-center gap-2.5">
        <span className="text-sm text-[var(--color-text)] font-medium tabular-nums">{value}</span>
        <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${ok ? 'bg-[#34d399]' : 'bg-[#f87171]'}`} aria-hidden />
      </div>
    </div>
  );
}

function MetricTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="surface-elevated p-4 min-h-[88px] flex flex-col">
      <span className="label-xs block mb-2">{label}</span>
      <span className="text-sm font-semibold text-[var(--color-text)] tabular-nums mt-auto">{value}</span>
    </div>
  );
}

export default function SettingsPage() {
  const [health, setHealth] = useState<{
    version?: string;
    environment?: string;
    database?: { status: string; database?: string };
    uptime_seconds?: number;
  } | null>(null);
  const [modelInfo, setModelInfo] = useState<ModelInfo | null>(null);

  useEffect(() => {
    healthAPI.check().then((res) => setHealth(res.data)).catch(console.error);
    healthAPI.modelInfo().then((res) => setModelInfo(res.data.data)).catch(console.error);
  }, []);

  const metrics = modelInfo?.metrics.models;

  return (
    <div className="page-stack">
      <PageHeader title="Settings" subtitle="System status, model metrics, and project roadmap" />

      <div className="grid grid-cols-1 lg:grid-cols-2 grid-gap-lg">
        <SectionCard title="Performance" icon={Gauge}>
          <div className="grid grid-cols-2 gap-4">
            <MetricTile
              label="Avg inference"
              value={
                modelInfo?.performance.average_inference_ms != null
                  ? `${modelInfo.performance.average_inference_ms} ms`
                  : 'Available after scans'
              }
            />
            <MetricTile
              label="P95 API latency"
              value={modelInfo?.performance.api_p95_ms ? `${modelInfo.performance.api_p95_ms} ms` : '—'}
            />
            <MetricTile
              label="Batch scanning"
              value={`${modelInfo?.performance.batch_scan_limit ?? 10} emails/request`}
            />
            <MetricTile label="Async API" value="Enabled" />
          </div>
        </SectionCard>

        <SectionCard title="Infrastructure" icon={Database}>
          <div className="space-y-2">
            <SettingRow label="Database" value={health?.database?.database || 'phishguard'} ok={health?.database?.status === 'connected'} />
            <SettingRow label="Backend" value="MongoDB Atlas" />
            <SettingRow label="API version" value={health?.version || '1.0.0'} />
            <SettingRow label="Environment" value={health?.environment || 'development'} />
            <SettingRow label="Uptime" value={health?.uptime_seconds ? `${Math.floor(health.uptime_seconds / 60)}m` : '—'} />
          </div>
        </SectionCard>

        <SectionCard title="ML evaluation metrics" icon={Cpu}>
          {metrics ? (
            <div className="space-y-3">
              <p className="text-xs text-[var(--color-text-muted)] leading-relaxed pb-1">{modelInfo?.metrics.evaluation.note}</p>
              {[
                ['Logistic Regression', metrics.logistic_regression.f1_weighted, metrics.logistic_regression.f1_std],
                ['Random Forest', metrics.random_forest.f1_weighted, metrics.random_forest.f1_std],
                ['DistilBERT', metrics.distilbert.f1_weighted, null],
              ].map(([name, f1, std]) => (
                <div key={name as string} className="flex items-center justify-between px-4 py-3.5 surface-elevated min-h-[52px]">
                  <span className="text-sm text-[var(--color-text-secondary)]">{name}</span>
                  <span className="text-sm font-semibold text-[var(--color-accent)] tabular-nums">
                    {f1 != null ? `F1 ${(f1 as number).toFixed(2)}${std != null ? ` ± ${(std as number).toFixed(2)}` : ''}` : 'Configurable'}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-[var(--color-text-muted)]">Loading metrics...</p>
          )}
        </SectionCard>

        <SectionCard title="Roadmap" icon={Map}>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {ROADMAP.map((item) => (
              <div key={item} className="flex items-center gap-2.5 px-4 py-3 surface-elevated text-sm text-[var(--color-text-secondary)] min-h-[44px]">
                <span className="text-[var(--color-text-muted)] shrink-0">·</span>
                {item}
              </div>
            ))}
          </div>
        </SectionCard>
      </div>
    </div>
  );
}
