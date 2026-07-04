"""
PhishGuard AI — Hybrid AI Pipeline Orchestrator

Runs all detection layers in sequence and produces a unified, weighted prediction:
1. Rule-Based Engine → instant pattern matching
2. TF-IDF + ML Classifiers → fast statistical analysis
3. Transformer Classifier → deep semantic understanding (optional)
4. LLM Explainer → human-readable security report
"""

import time
import json
import structlog
from typing import Any

from app.ai.rule_engine import RuleEngine
from app.ai.ml_classifier import MLClassifier
from app.ai.transformer_classifier import TransformerClassifier
from app.ai.llm_explainer import LLMExplainer
from app.ai.nlp_features import NLPFeatureExtractor
from app.ai.url_analyzer import URLAnalyzer
from app.ai.sender_analyzer import SenderAnalyzer
from app.ai.highlighter import TextHighlighter

logger = structlog.get_logger(__name__)

# Ensemble weights for combining model predictions
MODEL_WEIGHTS = {
    "rule_engine": 0.25,
    "ml_classifier": 0.35,
    "transformer": 0.40,
}

# Fallback weights when transformer is not available
FALLBACK_WEIGHTS = {
    "rule_engine": 0.35,
    "ml_classifier": 0.65,
}


class PhishingPipeline:
    """Orchestrates the full hybrid AI phishing detection pipeline."""

    def __init__(self):
        logger.info("pipeline_initializing")
        self.rule_engine = RuleEngine()
        self.ml_classifier = MLClassifier()
        self.transformer = TransformerClassifier()
        self.llm_explainer = LLMExplainer()
        self.nlp_extractor = NLPFeatureExtractor()
        self.url_analyzer = URLAnalyzer()
        self.sender_analyzer = SenderAnalyzer()
        self.highlighter = TextHighlighter()
        logger.info("pipeline_initialized")

    async def analyze(
        self,
        subject: str,
        sender: str,
        receiver: str,
        body: str,
    ) -> dict[str, Any]:
        """Run the full analysis pipeline on an email."""
        start_time = time.perf_counter()

        # Combine subject and body for full text analysis
        full_text = f"Subject: {subject}\n\n{body}"
        combined_for_classification = f"{subject} {body}"

        # ── Layer 1: Rule-Based Analysis ────────────────────
        rule_start = time.perf_counter()
        rule_matches = self.rule_engine.analyze(full_text)
        rule_label, rule_probs = self.rule_engine.classify(rule_matches)
        rule_risk = self.rule_engine.compute_risk_score(rule_matches)
        rule_latency = (time.perf_counter() - rule_start) * 1000

        indicators = [
            {
                "name": m.name, "category": m.category, "severity": m.severity,
                "confidence": m.confidence, "matched_text": m.matched_text,
                "description": m.description,
            }
            for m in rule_matches
        ]

        # ── Layer 2: ML Classification ──────────────────────
        ml_start = time.perf_counter()
        ml_result = self.ml_classifier.predict(combined_for_classification)
        ml_latency = (time.perf_counter() - ml_start) * 1000
        ml_features = self.ml_classifier.get_feature_importance(combined_for_classification)

        # ── Layer 3: Transformer Classification (optional) ──
        trans_start = time.perf_counter()
        trans_result = self.transformer.predict(combined_for_classification)
        trans_latency = (time.perf_counter() - trans_start) * 1000

        # ── Ensemble: Weighted Combination ──────────────────
        classification, confidence, probabilities = self._ensemble(
            rule_probs, ml_result, trans_result,
        )

        # ── NLP Feature Extraction ──────────────────────────
        nlp_features = self.nlp_extractor.extract(full_text)

        # ── URL Analysis ────────────────────────────────────
        urls_analysis = self.url_analyzer.extract_and_analyze(full_text)

        # ── Sender Analysis ─────────────────────────────────
        display_name = ""
        if "<" in sender:
            parts = sender.split("<")
            display_name = parts[0].strip().strip('"')
        sender_analysis = self.sender_analyzer.analyze(sender, display_name)

        # ── Text Highlighting ───────────────────────────────
        highlights = self.highlighter.highlight(body)

        # ── Risk Score ──────────────────────────────────────
        risk_score = self._compute_final_risk(
            rule_risk, probabilities, urls_analysis, sender_analysis, nlp_features,
        )

        # ── LLM Security Report ────────────────────────────
        indicator_dicts = indicators[:15]
        security_report = await self.llm_explainer.generate_report(
            full_text, indicator_dicts, classification,
            sender_info=sender_analysis, url_info=urls_analysis,
        )

        # ── LLM Explanation ────────────────────────────────
        explanation = await self.llm_explainer.generate_explanation(
            full_text, indicator_dicts, classification,
        )

        # ── Model Results for Comparison ───────────────────
        model_results = [
            {
                "model_name": "Rule Engine",
                "classification": rule_label,
                "confidence": max(rule_probs.values()),
                "probabilities": rule_probs,
                "latency_ms": round(rule_latency, 2),
                "features": {"matched_rules": len(rule_matches), "risk_score": rule_risk},
            },
            {
                "model_name": "TF-IDF + ML Ensemble",
                "classification": ml_result["classification"],
                "confidence": ml_result["confidence"],
                "probabilities": ml_result["probabilities"],
                "latency_ms": round(ml_latency, 2),
                "features": {"top_features": ml_features[:5]},
            },
        ]

        if trans_result.get("available", True) and trans_result["classification"] != "unknown":
            model_results.append({
                "model_name": f"Transformer ({self.transformer.model_name})",
                "classification": trans_result["classification"],
                "confidence": trans_result["confidence"],
                "probabilities": trans_result["probabilities"],
                "latency_ms": round(trans_latency, 2),
                "features": {},
            })

        processing_time = (time.perf_counter() - start_time) * 1000

        return {
            "classification": classification,
            "confidence": round(confidence, 4),
            "risk_score": round(risk_score, 2),
            "probabilities": {k: round(v, 4) for k, v in probabilities.items()},
            "indicators": indicators,
            "urls_analysis": urls_analysis,
            "sender_analysis": sender_analysis,
            "nlp_features": nlp_features,
            "explanation": explanation,
            "security_report": security_report,
            "highlights": highlights,
            "model_results": model_results,
            "processing_time_ms": round(processing_time, 2),
        }

    def _ensemble(
        self,
        rule_probs: dict[str, float],
        ml_result: dict,
        trans_result: dict,
    ) -> tuple[str, float, dict[str, float]]:
        """Combine predictions from all models using weighted voting."""
        ml_probs = ml_result.get("probabilities", {})

        if trans_result.get("available", True) and trans_result["classification"] != "unknown":
            trans_probs = trans_result.get("probabilities", {})
            weights = MODEL_WEIGHTS
        else:
            trans_probs = {}
            weights = FALLBACK_WEIGHTS

        # Weighted average of probabilities
        labels = ["safe", "suspicious", "phishing"]
        combined = {}

        for label in labels:
            score = 0.0
            total_weight = 0.0

            score += weights.get("rule_engine", 0) * rule_probs.get(label, 0)
            total_weight += weights.get("rule_engine", 0)

            score += weights.get("ml_classifier", 0) * ml_probs.get(label, 0)
            total_weight += weights.get("ml_classifier", 0)

            if trans_probs:
                score += weights.get("transformer", 0) * trans_probs.get(label, 0)
                total_weight += weights.get("transformer", 0)

            combined[label] = score / total_weight if total_weight > 0 else 0.33

        # Normalize
        total = sum(combined.values())
        if total > 0:
            combined = {k: v / total for k, v in combined.items()}

        classification = max(combined, key=combined.get)
        confidence = combined[classification]

        return classification, confidence, combined

    def _compute_final_risk(
        self,
        rule_risk: float,
        probabilities: dict[str, float],
        urls: list[dict],
        sender: dict,
        nlp: dict,
    ) -> float:
        """Compute final risk score (0-100) combining all signals."""
        # Base from classification probabilities
        phishing_prob = probabilities.get("phishing", 0)
        suspicious_prob = probabilities.get("suspicious", 0)
        prob_risk = (phishing_prob * 100) + (suspicious_prob * 40)

        # URL risk
        url_risk = 0
        if urls:
            avg_url_score = sum(u.get("suspicious_score", 0) for u in urls) / len(urls)
            url_risk = avg_url_score * 30

        # Sender risk
        sender_risk = max(0, (100 - sender.get("trust_score", 100)) * 0.3)

        # Urgency risk
        urgency_risk = nlp.get("urgency_score", 0) * 20

        # Weighted combination
        final = (
            prob_risk * 0.40
            + rule_risk * 0.25
            + url_risk * 0.15
            + sender_risk * 0.10
            + urgency_risk * 0.10
        )

        return min(100.0, max(0.0, final))

    def get_model_status(self) -> dict[str, str]:
        """Get the status of all pipeline models."""
        return {
            "rule_engine": "active",
            "ml_classifier": "trained" if self.ml_classifier.is_trained else "fallback",
            "transformer": self.transformer.status,
            "llm_explainer": self.llm_explainer.status,
        }

    def get_model_info(self) -> dict[str, Any]:
        """Return model status, evaluation metrics, and hybrid architecture metadata."""
        from app.ai.model_metrics import build_platform_info, load_model_metrics

        metrics = load_model_metrics()
        platform = build_platform_info()
        perf = platform["performance"]

        return {
            "status": self.get_model_status(),
            "metrics": metrics,
            "hybrid_architecture": {
                "summary": (
                    "Rather than relying on a single classifier, PhishGuard combines "
                    "rule-based heuristics, classical ML, transformer semantics, and "
                    "LLM reasoning to improve interpretability while maintaining low latency."
                ),
                "layers": [
                    {
                        "name": "Rule Engine",
                        "role": "Deterministic threat indicators via 29 regex rules",
                        "latency_ms": "~5",
                    },
                    {
                        "name": "ML Classifier",
                        "role": "Fast statistical classification (TF-IDF + LR + RF ensemble)",
                        "latency_ms": "~50",
                    },
                    {
                        "name": "Transformer",
                        "role": "Semantic understanding via DistilBERT (configurable)",
                        "latency_ms": "~500",
                    },
                    {
                        "name": "LLM Explainer",
                        "role": "Analyst-style security report generation",
                        "latency_ms": "~2000",
                    },
                ],
            },
            "performance": perf,
            "explainability": platform["explainability"],
            "production_engineering": platform["platform"]["architecture"],
        }
