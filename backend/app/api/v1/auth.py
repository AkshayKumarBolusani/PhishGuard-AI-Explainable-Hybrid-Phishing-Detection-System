"""PhishGuard AI — Auth API Routes"""
from fastapi import APIRouter, Depends, HTTPException
from app.api.v1.deps import require_auth
from app.schemas.auth import UserRegister, UserLogin, APIKeyCreate
from app.services.auth_service import AuthService
from app.core.exceptions import AppException

router = APIRouter(prefix="/auth", tags=["Authentication"])
auth_service = AuthService()


@router.post("/register", summary="Register a new user")
async def register(data: UserRegister):
    try:
        profile = auth_service.register(data.email, data.username, data.password, data.full_name)
        return {"status": "success", "data": profile}
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/login", summary="Login and get access token")
async def login(data: UserLogin):
    try:
        result = auth_service.login(data.email, data.password)
        return {"status": "success", "data": result}
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/profile", summary="Get current user profile")
async def get_profile(user: dict = Depends(require_auth)):
    try:
        profile = auth_service.get_profile(user["id"])
        return {"status": "success", "data": profile}
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/api-keys", summary="Create API key")
async def create_api_key(data: APIKeyCreate, user: dict = Depends(require_auth)):
    result = auth_service.create_api_key(user["id"], data.name)
    return {"status": "success", "data": result}


@router.get("/api-keys", summary="List API keys")
async def list_api_keys(user: dict = Depends(require_auth)):
    keys = auth_service.list_api_keys(user["id"])
    return {"status": "success", "data": keys}


@router.delete("/api-keys/{key_id}", summary="Delete API key")
async def delete_api_key(key_id: str, user: dict = Depends(require_auth)):
    try:
        auth_service.delete_api_key(key_id, user["id"])
        return {"status": "success", "message": "API key deleted"}
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
