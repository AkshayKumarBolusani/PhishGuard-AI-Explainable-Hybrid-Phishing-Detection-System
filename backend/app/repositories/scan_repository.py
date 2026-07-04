"""
PhishGuard AI — Scan Repository

Handles all scan result persistence and retrieval operations via MongoDB.
"""

import csv
import io
import json
from datetime import datetime, timezone
from typing import Any

from app.core.security import generate_uuid
from app.database.mongodb import (
    build_text_search_filter,
    get_collection,
    paginate_query,
)
from pymongo import ReturnDocument

from app.repositories.base import BaseRepository


class ScanRepository(BaseRepository):
    """Scan results data access layer backed by MongoDB."""

    COLLECTION = "scans"

    def __init__(self):
        self.collection = get_collection(self.COLLECTION)

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        record = {
            "id": data.get("id", generate_uuid()),
            "user_id": data.get("user_id", "anonymous"),
            "subject": data.get("subject", ""),
            "sender": data.get("sender", ""),
            "receiver": data.get("receiver", ""),
            "body": data.get("body", ""),
            "classification": data.get("classification", ""),
            "confidence": float(data.get("confidence", 0)),
            "risk_score": float(data.get("risk_score", 0)),
            "safe_probability": float(data.get("safe_probability", 0)),
            "suspicious_probability": float(data.get("suspicious_probability", 0)),
            "phishing_probability": float(data.get("phishing_probability", 0)),
            "indicators": self._coerce_json(data.get("indicators"), []),
            "urls_analysis": self._coerce_json(data.get("urls_analysis"), []),
            "sender_analysis": self._coerce_json(data.get("sender_analysis"), {}),
            "nlp_features": self._coerce_json(data.get("nlp_features"), {}),
            "explanation": data.get("explanation", ""),
            "security_report": self._coerce_json(data.get("security_report"), {}),
            "highlights": self._coerce_json(data.get("highlights"), []),
            "model_results": self._coerce_json(data.get("model_results"), {}),
            "processing_time_ms": float(data.get("processing_time_ms", 0)),
            "is_favorite": bool(data.get("is_favorite", False)),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.collection.insert_one(record)
        return record

    def get_by_id(self, record_id: str) -> dict[str, Any] | None:
        return self.collection.find_one({"id": record_id}, {"_id": 0})

    def get_all(
        self,
        filters: dict[str, str] | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str | None = None,
        sort_desc: bool = True,
    ) -> tuple[list[dict[str, Any]], int]:
        query: dict[str, Any] = dict(filters or {})
        query.update(
            build_text_search_filter(search, ["subject", "sender", "body", "classification"])
        )
        return paginate_query(
            self.collection,
            query,
            sort_by=sort_by or "created_at",
            sort_desc=sort_desc,
            page=page,
            page_size=page_size,
        )

    def get_by_user(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        classification: str | None = None,
        search: str | None = None,
    ) -> tuple[list[dict[str, Any]], int]:
        filters: dict[str, str] = {"user_id": user_id}
        if classification:
            filters["classification"] = classification
        return self.get_all(
            filters=filters,
            search=search,
            page=page,
            page_size=page_size,
        )

    def update(self, record_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        return self.collection.find_one_and_update(
            {"id": record_id},
            {"$set": data},
            return_document=ReturnDocument.AFTER,
            projection={"_id": 0},
        )

    def delete(self, record_id: str) -> bool:
        result = self.collection.delete_one({"id": record_id})
        return result.deleted_count > 0

    def toggle_favorite(self, record_id: str) -> dict[str, Any] | None:
        row = self.get_by_id(record_id)
        if not row:
            return None
        new_fav = not bool(row.get("is_favorite"))
        return self.update(record_id, {"is_favorite": new_fav})

    def count(self, filters: dict[str, str] | None = None) -> int:
        return self.collection.count_documents(filters or {})

    def find_by_user(self, user_id: str | None = None) -> list[dict[str, Any]]:
        query = {"user_id": user_id} if user_id else {}
        return list(self.collection.find(query, {"_id": 0}))

    def get_statistics(self, user_id: str | None = None) -> dict[str, Any]:
        """Compute dashboard statistics using MongoDB aggregation."""
        match_stage: dict[str, Any] = {}
        if user_id:
            match_stage["user_id"] = user_id

        pipeline: list[dict[str, Any]] = []
        if match_stage:
            pipeline.append({"$match": match_stage})

        pipeline.extend(
            [
                {
                    "$group": {
                        "_id": None,
                        "total_scans": {"$sum": 1},
                        "safe_count": {
                            "$sum": {"$cond": [{"$eq": ["$classification", "safe"]}, 1, 0]}
                        },
                        "suspicious_count": {
                            "$sum": {"$cond": [{"$eq": ["$classification", "suspicious"]}, 1, 0]}
                        },
                        "phishing_count": {
                            "$sum": {"$cond": [{"$eq": ["$classification", "phishing"]}, 1, 0]}
                        },
                        "average_risk_score": {"$avg": "$risk_score"},
                    }
                }
            ]
        )

        result = list(self.collection.aggregate(pipeline))
        if not result:
            return {
                "total_scans": 0,
                "safe_count": 0,
                "suspicious_count": 0,
                "phishing_count": 0,
                "average_risk_score": 0.0,
            }

        stats = result[0]
        return {
            "total_scans": stats.get("total_scans", 0),
            "safe_count": stats.get("safe_count", 0),
            "suspicious_count": stats.get("suspicious_count", 0),
            "phishing_count": stats.get("phishing_count", 0),
            "average_risk_score": round(float(stats.get("average_risk_score") or 0), 2),
        }

    def export_data(self, user_id: str | None = None, format: str = "csv") -> str:
        """Export scan data for a user as CSV or JSON."""
        query = {"user_id": user_id} if user_id else {}
        rows = list(self.collection.find(query, {"_id": 0}))

        if format == "json":
            return json.dumps(rows, indent=2, default=str)

        output = io.StringIO()
        if rows:
            fieldnames = list(rows[0].keys())
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow({k: self._export_value(v) for k, v in row.items()})
        return output.getvalue()

    @staticmethod
    def _coerce_json(value: Any, default: Any) -> Any:
        if value is None:
            return default
        if isinstance(value, (dict, list)):
            return value
        if isinstance(value, str):
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return default
        return default

    @staticmethod
    def _export_value(value: Any) -> str:
        if isinstance(value, (dict, list)):
            return json.dumps(value)
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value) if value is not None else ""
