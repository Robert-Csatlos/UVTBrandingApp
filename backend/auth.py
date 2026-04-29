import secrets
import bcrypt
from typing import Optional
from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session
from .database import get_db
from . import models

# In-memory session store: token → user_id
_sessions: dict[str, int] = {}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def create_session(user_id: int) -> str:
    token = secrets.token_hex(32)
    _sessions[token] = user_id
    return token


def delete_session(token: str) -> None:
    _sessions.pop(token, None)


def get_session_user_id(request: Request) -> Optional[int]:
    token = request.cookies.get("session_token")
    return _sessions.get(token) if token else None


def get_current_user(request: Request, db: Session = Depends(get_db)) -> models.User:
    token = request.cookies.get("session_token")
    if not token or token not in _sessions:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = _sessions[token]
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_superadmin(current_user: models.User = Depends(get_current_user)) -> models.User:
    if current_user.role != "SuperAdmin":
        raise HTTPException(status_code=403, detail="Only superadmin allowed")
    return current_user


def require_admin_or_above(current_user: models.User = Depends(get_current_user)) -> models.User:
    if current_user.role not in ("SuperAdmin", "Admin"):
        raise HTTPException(status_code=403, detail="Admin or SuperAdmin role required")
    return current_user


def require_coordinator_or_above(current_user: models.User = Depends(get_current_user)) -> models.User:
    if current_user.role not in ("SuperAdmin", "Admin", "Coordinator"):
        raise HTTPException(status_code=403, detail="Coordinator, Admin, or SuperAdmin role required")
    return current_user
