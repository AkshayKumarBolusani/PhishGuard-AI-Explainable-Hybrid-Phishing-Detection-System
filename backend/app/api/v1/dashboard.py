"""PhishGuard AI — Dashboard API Routes"""

from fastapi import APIRouter, Query

from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
dashboard_service = DashboardService()
USER_ID = "anonymous"


@router.get("/statistics", summary="Get dashboard statistics")
async def get_statistics():
    stats = dashboard_service.get_statistics(USER_ID)
    return {"status": "success", "data": stats}


@router.get("/trends", summary="Get threat trends")
async def get_trends(days: int = Query(30, ge=7, le=365)):
    trends = dashboard_service.get_trends(USER_ID, days)
    return {"status": "success", "data": trends}


@router.get("/attack-types", summary="Get attack type distribution")
async def get_attack_types():
    types = dashboard_service.get_attack_types(USER_ID)
    return {"status": "success", "data": types}
