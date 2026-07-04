"""PhishGuard AI — Scan API Routes"""

from fastapi import APIRouter, HTTPException

from app.schemas.email import BatchScanInput, EmailInput
from app.services.scan_service import ScanService

router = APIRouter(prefix="/scan", tags=["Scan"])
scan_service = ScanService()
USER_ID = "anonymous"


@router.post("", summary="Scan a single email")
async def scan_email(email: EmailInput):
    result = await scan_service.scan_email(
        subject=email.subject,
        sender=email.sender,
        receiver=email.receiver,
        body=email.body,
        user_id=USER_ID,
    )
    return {"status": "success", "data": result}


@router.post("/batch", summary="Scan multiple emails")
async def scan_batch(batch: BatchScanInput):
    emails = [e.model_dump() for e in batch.emails]
    results = await scan_service.scan_batch(emails, user_id=USER_ID)
    return {"status": "success", "data": results, "count": len(results)}


@router.get("/{scan_id}", summary="Get scan result by ID")
async def get_scan(scan_id: str):
    result = scan_service.get_scan(scan_id)
    if not result:
        raise HTTPException(status_code=404, detail="Scan not found")
    return {"status": "success", "data": result}


@router.delete("/{scan_id}", summary="Delete a scan")
async def delete_scan(scan_id: str):
    if not scan_service.delete_scan(scan_id):
        raise HTTPException(status_code=404, detail="Scan not found")
    return {"status": "success", "message": "Scan deleted"}


@router.post("/{scan_id}/favorite", summary="Toggle scan favorite")
async def toggle_favorite(scan_id: str):
    result = scan_service.toggle_favorite(scan_id)
    if not result:
        raise HTTPException(status_code=404, detail="Scan not found")
    return {"status": "success", "is_favorite": bool(result.get("is_favorite"))}
