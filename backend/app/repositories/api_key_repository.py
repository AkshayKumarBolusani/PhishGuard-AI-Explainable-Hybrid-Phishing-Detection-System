"""
PhishGuard AI — API Key Repository
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


class APIKeyRepository(BaseRepository):
    COLLECTION = "api_keys"

    def __init__(self):
        self.collection = get_collection(self.COLLECTION)

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        record = {
            "id": generate_uuid(),
            "user_id": data["user_id"],
            "key_hash": data["key_hash"],
            "key_prefix": data["key_prefix"],
            "name": data.get("name", "default"),
            "is_active": True,
            "created_at": datetime.now(UTC).isoformat(),
            "last_used": None,
            "expires_at": data.get("expires_at"),
        }
        self.collection.insert_one(record)
        return record

    def get_by_id(self, record_id: str) -> dict[str, Any] | None:
        return self.collection.find_one({"id": record_id}, {"_id": 0})

    def get_by_key_hash(self, key_hash: str) -> dict[str, Any] | None:
        return self.collection.find_one({"key_hash": key_hash}, {"_id": 0})

    def get_by_user(self, user_id: str) -> list[dict[str, Any]]:
        return list(
            self.collection.find({"user_id": user_id}, {"_id": 0}).sort("created_at", -1)
        )

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
        query.update(build_text_search_filter(search, ["name", "key_prefix"]))
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

    def update_last_used(self, key_id: str) -> None:
        self.collection.update_one(
            {"id": key_id},
            {"$set": {"last_used": datetime.now(UTC).isoformat()}},
        )
