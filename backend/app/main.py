"""
PhishGuard AI — FastAPI Application Entry Point

Production-ready FastAPI application with security middleware, structured logging,
rate limiting, and modular API routing.
"""

import time
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.exceptions import AppException
from app.core.logging import setup_logging
from app.core.middleware import (
    RateLimitMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
)
from app.database.init_db import init_database

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events — startup and shutdown."""
    # ── Startup ─────────────────────────────────────────────
    setup_logging()
    logger.info("application_starting", version=get_settings().app_version)

    # Initialize MongoDB
    init_database()

    # Try to train ML models if not already trained
    try:
        from app.ai.ml_classifier import MLClassifier
        classifier = MLClassifier()
        if not classifier.is_trained:
            logger.info("training_ml_models_on_startup")
            from app.ai.models.seed_data import get_seed_data
            texts, labels = get_seed_data()
            classifier.train(texts, labels)
            logger.info("ml_models_trained_successfully")
    except Exception as e:
        logger.warning("ml_training_skipped", error=str(e))

    logger.info("application_started")
    yield

    # ── Shutdown ────────────────────────────────────────────
    from app.database.init_db import shutdown_database

    shutdown_database()
    logger.info("application_shutting_down")


def create_app() -> FastAPI:
    """Application factory — creates and configures the FastAPI app."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description="AI-Powered Phishing Email Detection & Analysis Platform",
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── Middleware (order matters — last added runs first) ──
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(
        RateLimitMiddleware,
        calls_per_minute=settings.rate_limit_per_minute,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Exception Handlers ──────────────────────────────────
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(status_code=exc.status_code, content=exc.to_dict())

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error("unhandled_exception", error=str(exc), path=request.url.path)
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}},
        )

    # ── Routes ──────────────────────────────────────────────
    from app.api.v1.scan import router as scan_router
    from app.api.v1.history import router as history_router
    from app.api.v1.dashboard import router as dashboard_router
    from app.api.v1.health import router as health_router

    app.include_router(scan_router, prefix="/api/v1")
    app.include_router(history_router, prefix="/api/v1")
    app.include_router(dashboard_router, prefix="/api/v1")
    app.include_router(health_router, prefix="/api/v1")

    # ── Root ────────────────────────────────────────────────
    @app.get("/", tags=["Root"])
    async def root():
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "status": "operational",
            "docs": "/docs",
        }

    return app


# Application instance
app = create_app()
