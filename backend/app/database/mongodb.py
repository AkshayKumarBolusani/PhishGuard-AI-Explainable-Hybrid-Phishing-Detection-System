"""
PhishGuard AI — MongoDB Connection Manager

Provides a singleton MongoDB client with connection pooling and health checks.
"""

from __future__ import annotations

import re
from typing import Any

import certifi
import structlog
from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import ConnectionFailure

from app.core.config import get_settings

logger = structlog.get_logger(__name__)

_client: MongoClient | None = None
_db: Database | None = None


def _use_mongomock() -> bool:
    settings = get_settings()
    return settings.app_env == "test" or settings.mongodb_use_mock


def connect_mongodb() -> Database:
    """Initialize MongoDB connection and return the database handle."""
    global _client, _db

    if _db is not None:
        return _db

    settings = get_settings()

    if _use_mongomock():
        import mongomock

        _client = mongomock.MongoClient()
        _db = _client[settings.mongodb_db_name]
        logger.info("mongodb_connected", mode="mock", database=settings.mongodb_db_name)
        return _db

    if not settings.mongodb_url:
        raise ConnectionFailure("MONGODB_URL is required when not running in test/mock mode")

    _client = MongoClient(
        settings.mongodb_url,
        serverSelectionTimeoutMS=settings.mongodb_server_selection_timeout_ms,
        maxPoolSize=settings.mongodb_max_pool_size,
        retryWrites=True,
        tlsCAFile=certifi.where(),
    )

    try:
        _client.admin.command("ping")
    except ConnectionFailure as exc:
        _client.close()
        _client = None
        raise ConnectionFailure(f"Failed to connect to MongoDB: {exc}") from exc

    _db = _client[settings.mongodb_db_name]
    logger.info("mongodb_connected", mode="live", database=settings.mongodb_db_name)
    return _db


def get_database() -> Database:
    """Return the active database, connecting if needed."""
    if _db is None:
        return connect_mongodb()
    return _db


def get_collection(name: str) -> Collection:
    """Return a MongoDB collection by name."""
    return get_database()[name]


def close_mongodb() -> None:
    """Close the MongoDB client connection."""
    global _client, _db
    if _client is not None:
        _client.close()
        logger.info("mongodb_disconnected")
    _client = None
    _db = None


def mongodb_health() -> dict[str, Any]:
    """Return MongoDB connectivity status for health checks."""
    try:
        db = get_database()
        db.command("ping")
        return {"status": "connected", "database": db.name}
    except Exception as exc:
        return {"status": "disconnected", "error": str(exc)}


def build_text_search_filter(search: str | None, fields: list[str]) -> dict[str, Any]:
    """Build a case-insensitive regex filter across multiple fields."""
    if not search or not fields:
        return {}

    escaped = re.escape(search.strip())
    if not escaped:
        return {}

    return {
        "$or": [{field: {"$regex": escaped, "$options": "i"}} for field in fields],
    }


def build_sort(sort_by: str | None, sort_desc: bool) -> list[tuple[str, int]]:
    """Build MongoDB sort specification."""
    if not sort_by:
        return [("created_at", DESCENDING)]
    direction = DESCENDING if sort_desc else ASCENDING
    return [(sort_by, direction)]


def paginate_query(
    collection: Collection,
    query: dict[str, Any],
    *,
    sort_by: str | None = None,
    sort_desc: bool = False,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[dict[str, Any]], int]:
    """Execute a paginated query and return documents with total count."""
    total = collection.count_documents(query)
    cursor = (
        collection.find(query)
        .sort(build_sort(sort_by, sort_desc))
        .skip(max(page - 1, 0) * page_size)
        .limit(page_size)
    )
    return [_serialize_document(doc) for doc in cursor], total


def _serialize_document(document: dict[str, Any]) -> dict[str, Any]:
    """Convert MongoDB document to API-friendly dict (strip _id)."""
    result = dict(document)
    result.pop("_id", None)
    return result


def ensure_indexes() -> None:
    """Create indexes for all collections."""
    db = get_database()

    db.users.create_index("email", unique=True)
    db.users.create_index("username", unique=True)
    db.users.create_index([("created_at", DESCENDING)])

    db.scans.create_index("id", unique=True)
    db.scans.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
    db.scans.create_index("classification")
    try:
        db.scans.create_index([("subject", "text"), ("sender", "text"), ("body", "text")])
    except Exception as exc:
        logger.warning("text_index_skipped", error=str(exc))

    db.feedback.create_index("id", unique=True)
    db.feedback.create_index([("scan_id", ASCENDING), ("created_at", DESCENDING)])
    db.feedback.create_index("user_id")

    db.api_keys.create_index("id", unique=True)
    db.api_keys.create_index("key_hash")
    db.api_keys.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])

    logger.info("mongodb_indexes_ensured")
