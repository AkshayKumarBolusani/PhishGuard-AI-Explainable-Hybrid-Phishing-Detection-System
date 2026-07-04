"""
PhishGuard AI — User Repository

Handles all user data persistence operations via MongoDB.
"""

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


class UserRepository(BaseRepository):
    """User data access layer backed by MongoDB."""

    COLLECTION = "users"

    def __init__(self):
        self.collection = get_collection(self.COLLECTION)

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        record = {
            "id": generate_uuid(),
            "email": data["email"].lower().strip(),
            "username": data["username"].strip(),
            "hashed_password": data["hashed_password"],
            "full_name": data.get("full_name", ""),
            "role": data.get("role", "user"),
            "is_active": True,
            "created_at": now,
            "updated_at": now,
            "last_login": None,
        }
        self.collection.insert_one(record)
        return record

    def get_by_id(self, record_id: str) -> dict[str, Any] | None:
        return self.collection.find_one({"id": record_id}, {"_id": 0})

    def get_by_email(self, email: str) -> dict[str, Any] | None:
        return self.collection.find_one({"email": email.lower().strip()}, {"_id": 0})

    def get_by_username(self, username: str) -> dict[str, Any] | None:
        return self.collection.find_one({"username": username.lower().strip()}, {"_id": 0})

    def get_all(
        self,
        filters: dict[str, str] | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str | None = None,
        sort_desc: bool = False,
    ) -> tuple[list[dict[str, Any]], int]:
        query: dict[str, Any] = dict(filters or {})
        query.update(build_text_search_filter(search, ["email", "username", "full_name"]))
        return paginate_query(
            self.collection,
            query,
            sort_by=sort_by or "created_at",
            sort_desc=sort_desc,
            page=page,
            page_size=page_size,
        )

    def update(self, record_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        data = {**data, "updated_at": datetime.now(timezone.utc).isoformat()}
        result = self.collection.find_one_and_update(
            {"id": record_id},
            {"$set": data},
            return_document=ReturnDocument.AFTER,
            projection={"_id": 0},
        )
        return result

    def delete(self, record_id: str) -> bool:
        result = self.collection.delete_one({"id": record_id})
        return result.deleted_count > 0

    def count(self, filters: dict[str, str] | None = None) -> int:
        return self.collection.count_documents(filters or {})

    def update_last_login(self, user_id: str) -> None:
        self.collection.update_one(
            {"id": user_id},
            {"$set": {"last_login": datetime.now(timezone.utc).isoformat()}},
        )
