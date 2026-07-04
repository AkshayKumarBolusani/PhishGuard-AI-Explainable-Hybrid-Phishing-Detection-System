"""PhishGuard AI — Health API Routes"""

import time

from fastapi import APIRouter, Query

from app.ai.model_metrics import PerformanceTracker, build_platform_info, load_model_metrics
from app.core.config import get_settings
from app.schemas.dashboard import FeedbackInput
from app.services.dashboard_service import DashboardService
from app.services.feedback_service import FeedbackService
from app.services.scan_service import ScanService

router = APIRouter(tags=["Feedback & Health"])
feedback_service = FeedbackService()
scan_service = ScanService()
_start_time = time.time()


@router.post("/feedback", summary="Submit prediction feedback")
async def submit_feedback(data: FeedbackInput):
    record = feedback_service.submit_feedback(
        data.scan_id, "anonymous", data.is_correct, data.correct_label, data.feedback_text,
    )
    return {"status": "success", "data": record}


@router.get("/feedback", summary="List feedback")
async def list_feedback(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)):
    items, total = feedback_service.get_feedback(page, page_size)
    return {"status": "success", "data": {"items": items, "total": total}}


@router.get("/health", summary="Health check")
async def health_check():
    from app.database.mongodb import mongodb_health

    settings = get_settings()
    db_status = mongodb_health()
    overall = "healthy" if db_status.get("status") == "connected" else "degraded"
    return {
        "status": overall,
        "version": settings.app_version,
        "environment": settings.app_env,
        "database": db_status,
        "models": scan_service.get_model_status(),
        "uptime_seconds": round(time.time() - _start_time, 2),
    }


@router.get("/metrics", summary="Application metrics")
async def get_metrics():
    ds = DashboardService()
    stats = ds.get_statistics("anonymous")
    feedback = ds.get_feedback_stats()
    perf = PerformanceTracker.summary()
    platform = build_platform_info()
    return {
        "status": "success",
        "data": {
            "scans": stats,
            "feedback": feedback,
            "performance": platform["performance"],
            "latency_samples": perf,
            "uptime_seconds": round(time.time() - _start_time, 2),
        },
    }


@router.get("/models/status", summary="Get AI model status")
async def model_status():
    return {"status": "success", "data": scan_service.get_model_status()}


@router.get("/models/info", summary="Get AI model metrics and architecture")
async def model_info():
    return {"status": "success", "data": scan_service.get_model_info()}


@router.get("/models/metrics", summary="Get persisted model evaluation metrics")
async def model_metrics():
    return {"status": "success", "data": load_model_metrics()}
