"""
PhishGuard AI — Database Initialization

Connects to MongoDB and ensures indexes and model directories exist.
"""

import structlog

from app.core.config import get_settings
from app.database.mongodb import close_mongodb, connect_mongodb, ensure_indexes

logger = structlog.get_logger(__name__)


def init_database() -> None:
    """Initialize MongoDB connection, indexes, and local model directories."""
    settings = get_settings()

    model_dir = settings.model_save_path
    model_dir.mkdir(parents=True, exist_ok=True)

    connect_mongodb()
    ensure_indexes()

    logger.info("database_initialized", database=settings.mongodb_db_name)


def shutdown_database() -> None:
    """Close MongoDB connection on application shutdown."""
    close_mongodb()
