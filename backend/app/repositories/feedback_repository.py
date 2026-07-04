"""
PhishGuard AI — Feedback Repository

Stores user feedback on scan predictions for future model retraining.
"""

from datetime import UTC, datetime
from typing import Any

from pymongo import ReturnDocument

from app.core.security import generate_uuid
from app.database.mongodb import (
    build_text_search_filter,
    get_collection,
    paginate_query,
)
from app.repositories.base import BaseRepository


class FeedbackRepository(BaseRepository):
    COLLECTION = "feedback"

    def __init__(self):
        self.collection = get_collection(self.COLLECTION)

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        record = {
            "id": generate_uuid(),
            "scan_id": data["scan_id"],
            "user_id": data.get("user_id", "anonymous"),
            "correct_label": data.get("correct_label", ""),
            "feedback_text": data.get("feedback_text", ""),
            "is_correct": bool(data.get("is_correct", True)),
            "created_at": datetime.now(UTC).isoformat(),
        }
        self.collection.insert_one(record)
        return record

    def get_by_id(self, record_id: str) -> dict[str, Any] | None:
        return self.collection.find_one({"id": record_id}, {"_id": 0})

    def get_by_scan_id(self, scan_id: str) -> list[dict[str, Any]]:
        return list(self.collection.find({"scan_id": scan_id}, {"_id": 0}))

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
        query.update(build_text_search_filter(search, ["feedback_text", "correct_label"]))
        return paginate_query(
            self.collection,
            query,
            sort_by=sort_by or "created_at",
            sort_desc=sort_desc,
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

    def count(self, filters: dict[str, str] | None = None) -> int:
        return self.collection.count_documents(filters or {})

    def get_accuracy_stats(self) -> dict[str, Any]:
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_feedback": {"$sum": 1},
                    "correct_predictions": {
                        "$sum": {"$cond": [{"$eq": ["$is_correct", True]}, 1, 0]}
                    },
                }
            }
        ]
        result = list(self.collection.aggregate(pipeline))
        if not result:
            return {
                "total_feedback": 0,
                "correct_predictions": 0,
                "incorrect_predictions": 0,
                "accuracy": 0.0,
            }

        total = result[0]["total_feedback"]
        correct = result[0]["correct_predictions"]
        return {
            "total_feedback": total,
            "correct_predictions": correct,
            "incorrect_predictions": total - correct,
            "accuracy": round(correct / total * 100, 2) if total > 0 else 0.0,
        }
