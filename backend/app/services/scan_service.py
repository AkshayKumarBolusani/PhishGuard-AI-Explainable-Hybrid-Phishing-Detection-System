"""
PhishGuard AI — Scan Service

Orchestrates the scan workflow: validates input, runs AI pipeline, stores results.
"""

import json
from typing import Any

import structlog

from app.ai.pipeline import PhishingPipeline
from app.core.security import generate_uuid
from app.repositories.scan_repository import ScanRepository

logger = structlog.get_logger(__name__)

_pipeline: PhishingPipeline | None = None


def get_pipeline() -> PhishingPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = PhishingPipeline()
    return _pipeline


class ScanService:
    """Business logic for email scanning operations."""

    def __init__(self):
        self.scan_repo = ScanRepository()

    async def scan_email(
        self,
        subject: str,
        sender: str,
        receiver: str,
        body: str,
        user_id: str = "anonymous",
    ) -> dict[str, Any]:
        """Run the full scan pipeline and persist the result."""
        pipeline = get_pipeline()
        clean_body = self._sanitize_html(body)
        result = await pipeline.analyze(subject, sender, receiver, clean_body)
        scan_id = generate_uuid()

        record = {
            "id": scan_id,
            "user_id": user_id,
            "subject": subject[:500],
            "sender": sender[:250],
            "receiver": receiver[:250],
            "body": clean_body[:5000],
            "classification": result["classification"],
            "confidence": result["confidence"],
            "risk_score": result["risk_score"],
            "safe_probability": result["probabilities"].get("safe", 0),
            "suspicious_probability": result["probabilities"].get("suspicious", 0),
            "phishing_probability": result["probabilities"].get("phishing", 0),
            "indicators": result["indicators"],
            "urls_analysis": result["urls_analysis"],
            "sender_analysis": result["sender_analysis"],
            "nlp_features": result["nlp_features"],
            "explanation": result["explanation"],
            "security_report": result["security_report"],
            "highlights": result["highlights"],
            "model_results": result["model_results"],
            "processing_time_ms": result["processing_time_ms"],
        }
        self.scan_repo.create(record)

        result["id"] = scan_id
        logger.info(
            "scan_completed",
            scan_id=scan_id,
            classification=result["classification"],
            risk_score=result["risk_score"],
        )

        from app.ai.model_metrics import PerformanceTracker
        PerformanceTracker.record_inference(result["processing_time_ms"])

        return result

    async def scan_batch(
        self,
        emails: list[dict],
        user_id: str = "anonymous",
    ) -> list[dict[str, Any]]:
        results = []
        for email in emails:
            result = await self.scan_email(
                subject=email["subject"],
                sender=email["sender"],
                receiver=email.get("receiver", ""),
                body=email["body"],
                user_id=user_id,
            )
            results.append(result)
        return results

    def get_scan(self, scan_id: str) -> dict | None:
        row = self.scan_repo.get_by_id(scan_id)
        if not row:
            return None
        return self._parse_scan_row(row)

    def get_history(
        self,
        user_id: str | None = None,
        page: int = 1,
        page_size: int = 20,
        classification: str | None = None,
        search: str | None = None,
    ) -> tuple[list[dict], int]:
        filters = {}
        if user_id:
            filters["user_id"] = user_id
        if classification:
            filters["classification"] = classification

        rows, total = self.scan_repo.get_all(
            filters=filters if filters else None,
            search=search,
            page=page,
            page_size=page_size,
        )
        return [self._parse_scan_list_item(r) for r in rows], total

    def delete_scan(self, scan_id: str, user_id: str | None = None) -> bool:
        if user_id:
            row = self.scan_repo.get_by_id(scan_id)
            if not row or row.get("user_id") != user_id:
                return False
        return self.scan_repo.delete(scan_id)

    def toggle_favorite(self, scan_id: str, user_id: str | None = None) -> dict | None:
        row = self.scan_repo.get_by_id(scan_id)
        if not row:
            return None
        if user_id and row.get("user_id") != user_id:
            return None
        return self.scan_repo.toggle_favorite(scan_id)

    def export_history(self, user_id: str | None = None, format: str = "csv") -> str:
        return self.scan_repo.export_data(user_id, format)

    def get_model_status(self) -> dict[str, str]:
        return get_pipeline().get_model_status()

    def get_model_info(self) -> dict:
        return get_pipeline().get_model_info()

    def _sanitize_html(self, text: str) -> str:
        try:
            import bleach

            return bleach.clean(text, tags=[], strip=True)
        except ImportError:
            import re

            return re.sub(r"<[^>]+>", "", text)

    def _parse_scan_row(self, row: dict) -> dict:
        parsed = dict(row)
        json_fields = [
            "indicators",
            "urls_analysis",
            "sender_analysis",
            "nlp_features",
            "security_report",
            "highlights",
            "model_results",
        ]
        for field in json_fields:
            if field in parsed and isinstance(parsed[field], str):
                try:
                    parsed[field] = json.loads(parsed[field])
                except (json.JSONDecodeError, TypeError):
                    parsed[field] = (
                        {}
                        if field in ("sender_analysis", "nlp_features", "security_report", "model_results")
                        else []
                    )

        for num_field in [
            "confidence",
            "risk_score",
            "safe_probability",
            "suspicious_probability",
            "phishing_probability",
            "processing_time_ms",
        ]:
            try:
                parsed[num_field] = float(parsed.get(num_field, 0))
            except (ValueError, TypeError):
                parsed[num_field] = 0.0

        parsed["probabilities"] = {
            "safe": parsed.get("safe_probability", 0),
            "suspicious": parsed.get("suspicious_probability", 0),
            "phishing": parsed.get("phishing_probability", 0),
        }
        parsed["is_favorite"] = self._as_bool(parsed.get("is_favorite"))
        return parsed

    def _parse_scan_list_item(self, row: dict) -> dict:
        return {
            "id": row.get("id", ""),
            "subject": row.get("subject", ""),
            "sender": row.get("sender", ""),
            "classification": row.get("classification", ""),
            "confidence": float(row.get("confidence", 0)),
            "risk_score": float(row.get("risk_score", 0)),
            "is_favorite": self._as_bool(row.get("is_favorite")),
            "created_at": row.get("created_at", ""),
        }

    @staticmethod
    def _as_bool(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() == "true"
        return bool(value)
