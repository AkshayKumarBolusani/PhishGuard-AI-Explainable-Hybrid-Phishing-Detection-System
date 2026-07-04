"""PhishGuard AI — History API Routes"""

from fastapi import APIRouter, Query
from fastapi.responses import PlainTextResponse

from app.services.scan_service import ScanService

router = APIRouter(prefix="/history", tags=["History"])
scan_service = ScanService()
USER_ID = "anonymous"


@router.get("", summary="Get scan history")
async def get_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    classification: str | None = None,
    search: str | None = None,
):
    items, total = scan_service.get_history(USER_ID, page, page_size, classification, search)
    total_pages = (total + page_size - 1) // page_size
    return {
        "status": "success",
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        },
    }


@router.get("/export", summary="Export scan history")
async def export_history(format: str = Query("csv", pattern="^(csv|json)$")):
    content = scan_service.export_history(USER_ID, format)
    media = "text/csv" if format == "csv" else "application/json"
    return PlainTextResponse(
        content=content,
        media_type=media,
        headers={"Content-Disposition": f"attachment; filename=phishguard_export.{format}"},
    )
