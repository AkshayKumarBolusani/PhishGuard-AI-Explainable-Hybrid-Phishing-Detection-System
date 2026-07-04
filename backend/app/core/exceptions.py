"""
PhishGuard AI — Structured Exception Hierarchy

All application exceptions inherit from AppException for consistent error handling.
"""

from typing import Any


class AppException(Exception):
    """Base application exception with structured error data."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        return {
            "error": {
                "code": self.error_code,
                "message": self.message,
                "details": self.details,
            }
        }


class AuthenticationError(AppException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed", details: dict | None = None):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR",
            details=details,
        )


class AuthorizationError(AppException):
    """Raised when user lacks required permissions."""

    def __init__(self, message: str = "Insufficient permissions", details: dict | None = None):
        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR",
            details=details,
        )


class ValidationError(AppException):
    """Raised for input validation failures."""

    def __init__(self, message: str = "Validation failed", details: dict | None = None):
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class NotFoundError(AppException):
    """Raised when a requested resource is not found."""

    def __init__(self, resource: str = "Resource", resource_id: str = ""):
        super().__init__(
            message=f"{resource} not found",
            status_code=404,
            error_code="NOT_FOUND",
            details={"resource": resource, "id": resource_id},
        )


class RateLimitError(AppException):
    """Raised when rate limit is exceeded."""

    def __init__(self, retry_after: int = 60):
        super().__init__(
            message="Rate limit exceeded. Please try again later.",
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            details={"retry_after_seconds": retry_after},
        )


class AIModelError(AppException):
    """Raised when an AI model encounters an error."""

    def __init__(self, model_name: str, message: str = "Model inference failed"):
        super().__init__(
            message=f"AI Model Error ({model_name}): {message}",
            status_code=500,
            error_code="AI_MODEL_ERROR",
            details={"model": model_name},
        )


class DuplicateError(AppException):
    """Raised when attempting to create a duplicate resource."""

    def __init__(self, resource: str = "Resource", field: str = ""):
        super().__init__(
            message=f"{resource} already exists",
            status_code=409,
            error_code="DUPLICATE_ERROR",
            details={"resource": resource, "field": field},
        )
