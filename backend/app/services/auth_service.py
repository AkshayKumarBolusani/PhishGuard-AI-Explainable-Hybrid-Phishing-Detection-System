"""PhishGuard AI — Auth Service"""
import structlog
from app.core.exceptions import AuthenticationError, DuplicateError, NotFoundError
from app.core.security import (
    create_access_token, generate_api_key, generate_uuid,
    hash_password, verify_password,
)
from app.core.config import get_settings
from app.repositories.user_repository import UserRepository
from app.repositories.api_key_repository import APIKeyRepository

logger = structlog.get_logger(__name__)


class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.api_key_repo = APIKeyRepository()

    def register(self, email: str, username: str, password: str, full_name: str = "") -> dict:
        if self.user_repo.get_by_email(email):
            raise DuplicateError("User", "email")
        if self.user_repo.get_by_username(username):
            raise DuplicateError("User", "username")

        user = self.user_repo.create({
            "email": email.lower().strip(),
            "username": username.strip(),
            "hashed_password": hash_password(password),
            "full_name": full_name.strip(),
            "role": "user",
        })
        logger.info("user_registered", user_id=user["id"], email=email)
        return self._user_profile(user)

    def login(self, email: str, password: str) -> dict:
        user = self.user_repo.get_by_email(email.lower().strip())
        if not user or not verify_password(password, user["hashed_password"]):
            raise AuthenticationError("Invalid email or password")
        if user.get("is_active") is False or user.get("is_active") == "false":
            raise AuthenticationError("Account is disabled")

        self.user_repo.update_last_login(user["id"])

        settings = get_settings()
        token = create_access_token({"sub": user["id"], "email": user["email"]})
        profile = self._user_profile(user)

        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": settings.jwt_expiration_minutes * 60,
            "user": profile,
        }

    def get_profile(self, user_id: str) -> dict:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User", user_id)
        return self._user_profile(user)

    def create_api_key(self, user_id: str, name: str = "default") -> dict:
        key = generate_api_key()
        key_hash = hash_password(key)
        record = self.api_key_repo.create({
            "user_id": user_id, "key_hash": key_hash,
            "key_prefix": key[:20] + "...", "name": name,
        })
        return {"id": record["id"], "name": name, "key_prefix": record["key_prefix"],
                "created_at": record["created_at"], "key": key}

    def list_api_keys(self, user_id: str) -> list[dict]:
        keys = self.api_key_repo.get_by_user(user_id)
        return [{"id": k["id"], "name": k["name"], "key_prefix": k["key_prefix"],
                 "created_at": k["created_at"], "last_used": k.get("last_used", "")} for k in keys]

    def delete_api_key(self, key_id: str, user_id: str) -> bool:
        key = self.api_key_repo.get_by_id(key_id)
        if not key or key.get("user_id") != user_id:
            raise NotFoundError("API Key", key_id)
        return self.api_key_repo.delete(key_id)

    def _user_profile(self, user: dict) -> dict:
        return {
            "id": user["id"], "email": user["email"], "username": user["username"],
            "full_name": user.get("full_name", ""), "role": user.get("role", "user"),
            "created_at": user.get("created_at", ""),
        }
