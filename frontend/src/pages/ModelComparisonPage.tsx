import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  BarChart3, Cpu, Zap, Brain, CheckCircle2, AlertCircle, MinusCircle,
  Gauge, Layers, Shield,
} from 'lucide-react';
import { healthAPI } from '@/services/api';
import PageHeader from '@/components/ui/PageHeader';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import SectionCard from '@/components/ui/SectionCard';
import type { ModelInfo } from '@/types';

const MODEL_META: Record<string, { icon: typeof Cpu; desc: string }> = {
  rule_engine: { icon: Zap, desc: '29 regex rules across urgency, credential theft, and fraud categories.' },
  ml_classifier: { icon: BarChart3, desc: 'TF-IDF vectorization with Logistic Regression and Random Forest ensemble.' },
  transformer: { icon: Brain, desc: 'DistilBERT sequence classifier for semantic understanding (configurable).' },
  llm_explainer: { icon: Cpu, desc: 'Analyst-style security reports with evidence and recommendations.' },
};

function formatF1(value: number | null | undefined, std?: number | null): string {
  if (value == null) return 'N/A';
  if (std != null) return `${value.toFixed(2)} ± ${std.toFixed(2)}`;
  return value.toFixed(2);
}

function formatAcc(value: number | null | undefined, std?: number | null): string {
  if (value == null) return '—';
  const pct = (value * 100).toFixed(1);
  if (std != null) return `${pct}% ± ${(std * 100).toFixed(1)}%`;
  return `${pct}%`;
}

export default function ModelComparisonPage() {
  const [info, setInfo] = useState<ModelInfo | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    healthAPI.modelInfo().then((res) => setInfo(res.data.data)).catch(console.error).finally(() => setLoading(false));
  }, []);

  const statusConfig = (status: string) => {
    const s = status.toLowerCase();
    if (s === 'active' || s === 'trained' || s.includes('connected')) {
      return { color: '#34d399', icon: CheckCircle2 };
    }
    if (s.includes('fallback') || s.includes('mock')) {
      return { color: '#fbbf24', icon: AlertCircle };
    }
    return { color: '#71717a', icon: MinusCircle };
  };

  if (loading) return <LoadingSpinner label="Loading model metrics..." />;
  if (!info) return null;

  const { metrics, status, hybrid_architecture, performance, explainability } = info;
  const lr = metrics.models.logistic_regression;
  const rf = metrics.models.random_forest;
  const db = metrics.models.distilbert;

  return (
    <div className="page-stack">
      <PageHeader
        title="Model analysis"
        subtitle="Quantified metrics, hybrid architecture, and runtime performance"
      />

      <div className="surface overflow-hidden">
        <div className="card-header">
          <div className="flex items-center gap-2.5">
            <BarChart3 className="w-4 h-4 text-[var(--color-text-muted)]" strokeWidth={1.75} />
            <h3 className="text-sm font-medium text-[var(--color-text)]">Machine learning pipeline</h3>
          </div>
        </div>
        <div className="card-body-lg section-stack">
          <p className="text-xs text-[var(--color-text-muted)] leading-relaxed">
            130-email demonstration dataset · {metrics.evaluation.folds ?? 5}-fold CV · pipeline validation only
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-3 grid-gap-lg">
            {[
              { name: 'Logistic Regression', f1: lr.f1_weighted, f1Std: lr.f1_std, acc: lr.accuracy, accStd: lr.accuracy_std, detail: lr.vectorizer },
              { name: 'Random Forest', f1: rf.f1_weighted, f1Std: rf.f1_std, acc: rf.accuracy, accStd: rf.accuracy_std, detail: `${rf.estimators ?? 100} estimators, max depth ${rf.max_depth ?? 12}` },
              { name: 'DistilBERT', f1: db.f1_weighted, f1Std: null, acc: null, accStd: null, detail: db.note || 'Configurable — not enabled' },
            ].map((model) => (
              <div key={model.name} className="surface-elevated p-5 flex flex-col min-h-[140px]">
                <p className="text-sm font-medium text-[var(--color-text)]">{model.name}</p>
                <p className="text-2xl font-semibold text-[var(--color-accent)] mt-3 tabular-nums tracking-tight">
                  F1 {formatF1(model.f1, model.f1Std)}
                </p>
                {model.acc != null && (
                  <p className="text-xs text-[var(--color-text-muted)] mt-2 tabular-nums">Accuracy: {formatAcc(model.acc, model.accStd)}</p>
                )}
                <p className="text-[11px] text-[var(--color-text-muted)] mt-auto pt-4 leading-relaxed">{model.detail}</p>
              </div>
            ))}
          </div>
          <div className="surface-elevated p-4 text-sm text-[var(--color-text-secondary)] leading-relaxed">
            <span className="text-[var(--color-text)] font-medium">Ensemble:</span> {metrics.ensemble.method.replace(/_/g, ' ')} with{' '}
            {metrics.ensemble.confidence_calibration.toLowerCase()}. Weights: Rule Engine{' '}
            {(metrics.ensemble.weights_without_transformer.rule_engine * 100).toFixed(0)}% · ML{' '}
            {(metrics.ensemble.weights_without_transformer.ml_classifier * 100).toFixed(0)}%.
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 grid-gap-lg">
        {[
          { label: 'Avg inference', value: performance.average_inference_ms != null ? `${performance.average_inference_ms} ms` : 'Run scans to populate', icon: Gauge },
          { label: 'P95 inference', value: performance.inference_p95_ms != null ? `${performance.inference_p95_ms} ms` : '—', icon: Zap },
          { label: 'P95 API latency', value: performance.api_p95_ms != null ? `${performance.api_p95_ms} ms` : '—', icon: Layers },
          { label: 'Batch limit', value: `${performance.batch_scan_limit} emails`, icon: BarChart3 },
        ].map(({ label, value, icon: Icon }) => (
          <div key={label} className="surface metric-card">
            <div className="flex items-center gap-2">
              <Icon className="w-3.5 h-3.5 text-[var(--color-text-muted)] opacity-70" strokeWidth={1.75} />
              <span className="label-xs">{label}</span>
            </div>
            <p className="metric-value tabular-nums mt-auto pt-4 text-xl">{value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 grid-gap-lg">
        {Object.entries(status).map(([name, st]) => {
          const meta = MODEL_META[name] || { icon: Cpu, desc: '' };
          const cfg = statusConfig(st);
          const Icon = meta.icon;
          const StatusIcon = cfg.icon;
          return (
            <div key={name} className="surface surface-interactive p-5 min-h-[120px]">
              <div className="flex items-center justify-between mb-4">
                <div className="w-9 h-9 rounded-[var(--radius-md)] bg-[var(--color-accent-dim)] flex items-center justify-center">
                  <Icon className="w-4 h-4 text-[var(--color-accent)]" strokeWidth={1.75} />
                </div>
                <StatusIcon className="w-4 h-4" style={{ color: cfg.color }} strokeWidth={1.75} />
              </div>
              <h3 className="text-[var(--color-text)] font-medium capitalize text-sm">{name.replace(/_/g, ' ')}</h3>
              <p className="text-xs text-[var(--color-text-muted)] mt-1 capitalize">{st.replace(/_/g, ' ')}</p>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 grid-gap-lg">
        <SectionCard title="Hybrid AI architecture" icon={Layers} className="lg:col-span-2">
          <p className="text-body mb-6">{hybrid_architecture.summary}</p>
          <div className="space-y-5">
            {hybrid_architecture.layers.map((layer, i) => (
              <div key={layer.name} className="flex gap-4 items-start">
                <div className="w-7 h-7 rounded-[var(--radius-md)] bg-[var(--color-accent-dim)] text-[var(--color-accent)] flex items-center justify-center text-xs font-semibold shrink-0 tabular-nums">
                  {i + 1}
                </div>
                <div className="flex-1 min-w-0 pt-0.5">
                  <div className="flex items-center gap-3 flex-wrap">
                    <p className="text-[var(--color-text)] font-medium text-sm">{layer.name}</p>
                    <span className="text-[10px] mono text-[var(--color-text-muted)] tabular-nums">{layer.latency_ms}</span>
                  </div>
                  <p className="text-body mt-1">{layer.role}</p>
                </div>
              </div>
            ))}
          </div>
        </SectionCard>

        <div className="section-stack">
          <SectionCard title="Explainability" icon={Shield}>
            <ul className="space-y-2.5">
              {explainability.map((item) => (
                <li key={item} className="text-sm text-[var(--color-text-secondary)] flex gap-2.5 leading-relaxed">
                  <span className="text-[var(--color-text-muted)] shrink-0">·</span>
                  {item.replace(/_/g, ' ')}
                </li>
              ))}
            </ul>
          </SectionCard>

          <SectionCard title="Production engineering" icon={Cpu}>
            <ul className="space-y-2">
              {info.production_engineering.map((item) => (
                <li key={item} className="text-xs text-[var(--color-text-muted)] capitalize leading-relaxed pl-3 border-l border-[var(--color-border-subtle)]">{item.replace(/_/g, ' ')}</li>
              ))}
            </ul>
          </SectionCard>

          <div className="surface p-6 text-center">
            <p className="text-sm font-medium text-[var(--color-text)]">See live predictions</p>
            <Link to="/scanner" className="inline-flex mt-4 btn-accent">Open scanner</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
