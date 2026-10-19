"""
PhishGuard AI — Base Repository

Abstract base repository defining the standard CRUD interface.
All concrete repositories inherit from this class.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseRepository(ABC):
    """Abstract base repository with generic CRUD operations."""

    @abstractmethod
    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new record."""
        ...

    @abstractmethod
    def get_by_id(self, record_id: str) -> dict[str, Any] | None:
        """Retrieve a record by its ID."""
        ...

    @abstractmethod
    def get_all(
        self,
        filters: dict[str, str] | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str | None = None,
        sort_desc: bool = False,
    ) -> tuple[list[dict[str, Any]], int]:
        """Retrieve all records with optional filtering and pagination."""
        ...

    @abstractmethod
    def update(self, record_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        """Update an existing record."""
        ...

    @abstractmethod
    def delete(self, record_id: str) -> bool:
        """Delete a record by its ID."""
        ...

    @abstractmethod
    def count(self, filters: dict[str, str] | None = None) -> int:
        """Count records with optional filtering."""
        ...
