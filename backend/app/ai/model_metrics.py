"""
PhishGuard AI — Model Metrics & Performance Tracking

Persists evaluation metrics from training and runtime inference statistics.
"""

from __future__ import annotations

import json
import threading
from collections import deque
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import structlog

from app.core.config import get_settings

logger = structlog.get_logger(__name__)

METRICS_FILENAME = "model_metrics.json"
MAX_LATENCY_SAMPLES = 500


class PerformanceTracker:
    """Thread-safe rolling window for inference latency samples."""

    _lock = threading.Lock()
    _latencies_ms: deque[float] = deque(maxlen=MAX_LATENCY_SAMPLES)
    _api_latencies_ms: deque[float] = deque(maxlen=MAX_LATENCY_SAMPLES)

    @classmethod
    def record_inference(cls, latency_ms: float) -> None:
        with cls._lock:
            cls._latencies_ms.append(latency_ms)

    @classmethod
    def record_api_request(cls, latency_ms: float) -> None:
        with cls._lock:
            cls._api_latencies_ms.append(latency_ms)

    @classmethod
    def summary(cls) -> dict[str, Any]:
        with cls._lock:
            inference = list(cls._latencies_ms)
            api = list(cls._api_latencies_ms)

        def _stats(values: list[float]) -> dict[str, float | int]:
            if not values:
                return {"count": 0, "avg_ms": 0.0, "p50_ms": 0.0, "p95_ms": 0.0}
            sorted_vals = sorted(values)
            n = len(sorted_vals)
            p50 = sorted_vals[int(n * 0.5)]
            p95 = sorted_vals[min(int(n * 0.95), n - 1)]
            return {
                "count": n,
                "avg_ms": round(sum(sorted_vals) / n, 1),
                "p50_ms": round(p50, 1),
                "p95_ms": round(p95, 1),
            }

        return {
            "inference": _stats(inference),
            "api": _stats(api),
        }


def metrics_file_path() -> Path:
    return get_settings().model_save_path / METRICS_FILENAME


def save_model_metrics(metrics: dict[str, Any]) -> None:
    """Persist model evaluation metrics to disk."""
    path = metrics_file_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        **metrics,
        "updated_at": datetime.now(UTC).isoformat(),
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    logger.info("model_metrics_saved", path=str(path))


def load_model_metrics() -> dict[str, Any]:
    """Load persisted model metrics, or return defaults."""
    path = metrics_file_path()
    if not path.exists():
        return _default_metrics()
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("model_metrics_load_failed", error=str(exc))
        return _default_metrics()


def _default_metrics() -> dict[str, Any]:
    return {
        "dataset": {"samples": 0, "safe": 0, "suspicious": 0, "phishing": 0},
        "evaluation": {"method": "stratified_k_fold", "folds": 5, "note": "Metrics not yet computed — run training"},
        "models": {
            "logistic_regression": {"f1_weighted": None, "f1_std": None, "accuracy": None, "accuracy_std": None},
            "random_forest": {"f1_weighted": None, "f1_std": None, "accuracy": None, "accuracy_std": None},
            "distilbert": {"f1_weighted": None, "status": "configurable"},
        },
        "ensemble": {
            "method": "weighted_voting",
            "weights_without_transformer": {"rule_engine": 0.35, "ml_classifier": 0.65},
            "weights_with_transformer": {"rule_engine": 0.25, "ml_classifier": 0.35, "transformer": 0.40},
            "confidence_calibration": "probability normalization after weighted sum",
        },
    }


def build_platform_info() -> dict[str, Any]:
    """Aggregate platform capabilities for API responses."""
    from app.ai.rule_engine import RULES

    perf = PerformanceTracker.summary()
    inference_avg = perf["inference"]["avg_ms"] if perf["inference"]["count"] > 0 else None

    return {
        "performance": {
            "average_inference_ms": inference_avg,
            "inference_p95_ms": perf["inference"]["p95_ms"] if perf["inference"]["count"] > 0 else None,
            "api_p95_ms": perf["api"]["p95_ms"] if perf["api"]["count"] > 0 else None,
            "inference_sample_count": perf["inference"]["count"],
            "api_sample_count": perf["api"]["count"],
            "batch_scan_limit": 10,
            "async_endpoints": True,
            "mongodb_indexed_queries": True,
        },
        "platform": {
            "detection_rules": len(RULES),
            "rest_endpoints": 17,
            "ai_engines": 4,
            "architecture": [
                "repository_pattern",
                "service_layer",
                "dependency_injection",
                "structured_logging",
                "rate_limiting",
                "environment_configuration",
                "docker_deployment",
                "github_actions_ci",
            ],
        },
        "explainability": [
            "confidence_score",
            "triggered_phishing_indicators",
            "suspicious_urls",
            "nlp_entity_extraction",
            "feature_importance",
            "llm_generated_reasoning",
            "recommended_mitigation_steps",
        ],
    }
