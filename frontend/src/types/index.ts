/* Type definitions for PhishGuard AI */

export interface EmailInput {
  subject: string;
  sender: string;
  receiver: string;
  body: string;
}

export interface URLAnalysis {
  original_url: string;
  domain: string;
  tld: string;
  is_shortened: boolean;
  is_ip_address: boolean;
  is_https: boolean;
  is_homograph: boolean;
  suspicious_score: number;
  reasons: string[];
}

export interface SenderAnalysis {
  email: string;
  display_name: string;
  domain: string;
  is_free_provider: boolean;
  is_display_name_mismatch: boolean;
  is_typosquatting: boolean;
  spoofed_domain: string;
  trust_score: number;
  reasons: string[];
}

export interface NLPFeatures {
  entities: Record<string, string[]>;
  action_verbs: string[];
  imperative_sentences: string[];
  sentiment: { polarity: number; subjectivity: number };
  urgency_score: number;
  readability_score: number;
  emotion: string;
  word_count: number;
  sentence_count: number;
}

export interface SuspiciousIndicator {
  name: string;
  category: string;
  severity: string;
  confidence: number;
  matched_text: string;
  description: string;
}

export interface TextHighlight {
  start: number;
  end: number;
  text: string;
  category: string;
  severity: string;
}

export interface ModelResult {
  model_name: string;
  classification: string;
  confidence: number;
  probabilities: Record<string, number>;
  latency_ms: number;
  features: Record<string, any>;
}

export interface SecurityReport {
  executive_summary: string;
  risk_level: string;
  threat_indicators: string[];
  evidence: { indicator: string; detail: string }[];
  attack_type: string;
  likely_goal: string;
  recommended_actions: string[];
  user_advice: string;
  security_score: number;
  technical_notes: string;
}

export interface ScanResult {
  id: string;
  classification: 'safe' | 'suspicious' | 'phishing';
  confidence: number;
  risk_score: number;
  probabilities: Record<string, number>;
  indicators: SuspiciousIndicator[];
  urls_analysis: URLAnalysis[];
  sender_analysis: SenderAnalysis;
  nlp_features: NLPFeatures;
  explanation: string;
  security_report: SecurityReport;
  highlights: TextHighlight[];
  model_results: ModelResult[];
  processing_time_ms: number;
  created_at?: string;
}

export interface ScanListItem {
  id: string;
  subject: string;
  sender: string;
  classification: string;
  confidence: number;
  risk_score: number;
  is_favorite: boolean;
  created_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface DashboardStats {
  total_scans: number;
  safe_count: number;
  suspicious_count: number;
  phishing_count: number;
  average_risk_score: number;
  daily_scans: number;
  weekly_scans: number;
}

export interface ThreatTrend {
  date: string;
  safe: number;
  suspicious: number;
  phishing: number;
  total: number;
}

export interface AttackTypeCount {
  attack_type: string;
  count: number;
}

export interface UserProfile {
  id: string;
  email: string;
  username: string;
  full_name: string;
  role: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: UserProfile;
}

export type Classification = 'safe' | 'suspicious' | 'phishing';

export interface ModelMetrics {
  dataset: { samples: number; safe: number; suspicious: number; phishing: number };
  evaluation: { method: string; folds?: number; note: string };
  models: {
    logistic_regression: { f1_weighted: number | null; f1_std?: number | null; accuracy: number | null; accuracy_std?: number | null; vectorizer?: string };
    random_forest: { f1_weighted: number | null; f1_std?: number | null; accuracy: number | null; accuracy_std?: number | null; estimators?: number; max_depth?: number };
    distilbert: { f1_weighted: number | null; status: string; note?: string };
  };
  ensemble: {
    method: string;
    weights_without_transformer: Record<string, number>;
    confidence_calibration: string;
  };
}

export interface ModelInfo {
  status: Record<string, string>;
  metrics: ModelMetrics;
  hybrid_architecture: {
    summary: string;
    layers: { name: string; role: string; latency_ms: string }[];
  };
  performance: {
    average_inference_ms: number;
    inference_p95_ms: number;
    api_p95_ms: number;
    batch_scan_limit: number;
    async_endpoints: boolean;
    mongodb_indexed_queries: boolean;
  };
  explainability: string[];
  production_engineering: string[];
}
