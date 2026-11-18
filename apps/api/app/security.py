import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import get_db
from .models import AuthSession, User

bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    if len(password) < 8:
        raise ValueError("密码至少需要 8 位")
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 600_000)
    return f"pbkdf2_sha256$600000${base64.b64encode(salt).decode()}${base64.b64encode(digest).decode()}"


def verify_password(password: str, encoded: str) -> bool:
    algorithm, rounds, salt, expected = encoded.split("$", 3)
    if algorithm != "pbkdf2_sha256":
        return False
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), base64.b64decode(salt), int(rounds))
    return hmac.compare_digest(base64.b64encode(digest).decode(), expected)


def create_session(db: Session, user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    db.add(AuthSession(user_id=user_id, token_hash=hashlib.sha256(token.encode()).hexdigest(), expires_at=datetime.now(timezone.utc) + timedelta(days=30)))
    db.commit()
    return token


def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> User:
    if not credentials:
        raise HTTPException(401, "需要登录")
    token_hash = hashlib.sha256(credentials.credentials.encode()).hexdigest()
    session = db.scalar(select(AuthSession).where(AuthSession.token_hash == token_hash))
    if not session or session.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(401, "登录已失效")
    user = db.get(User, session.user_id)
    if not user:
        raise HTTPException(401, "用户不存在")
    return user

