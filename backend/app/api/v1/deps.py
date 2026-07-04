"""PhishGuard AI — Auth Dependencies"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.security import decode_access_token
from app.core.exceptions import AuthenticationError

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict | None:
    """Extract and validate the current user from JWT token. Returns None if no token."""
    if not credentials:
        return None
    try:
        payload = decode_access_token(credentials.credentials)
        return {"id": payload["sub"], "email": payload.get("email", "")}
    except AuthenticationError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")


async def require_auth(user: dict | None = Depends(get_current_user)) -> dict:
    """Require authentication — raises 401 if no valid token."""
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return user
