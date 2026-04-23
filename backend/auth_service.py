"""Auth service: email/password with bcrypt + JWT (30-day).

Keeps guest mode working in parallel. Decisions can be scoped by user_id (preferred for authed users)
or guest_id (for unauthed visitors).
"""
from __future__ import annotations

import os
import re
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import bcrypt
import jwt
from dotenv import load_dotenv
from fastapi import Depends, Header, HTTPException, status
from pydantic import BaseModel, EmailStr, Field, field_validator

load_dotenv(Path(__file__).parent / ".env")

JWT_SECRET = os.environ.get("JWT_SECRET") or "sda-dev-secret-change-me"
JWT_ALG = "HS256"
JWT_EXPIRE_DAYS = 30


# ------------------- Models -------------------
class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    name: Optional[str] = Field(default=None, max_length=80)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class PublicUser(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    created_at: datetime


class AuthResponse(BaseModel):
    token: str
    user: PublicUser


# ------------------- Password hashing -------------------
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


# ------------------- JWT -------------------
def create_token(user_id: str, email: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=JWT_EXPIRE_DAYS)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# ------------------- FastAPI dependencies -------------------
async def get_current_user_optional(
    authorization: Optional[str] = Header(default=None),
) -> Optional[Dict[str, Any]]:
    """Returns the JWT payload if present/valid, otherwise None."""
    if not authorization:
        return None
    m = re.match(r"^Bearer\s+(.+)$", authorization.strip(), re.IGNORECASE)
    token = m.group(1) if m else authorization.strip()
    payload = decode_token(token)
    return payload


async def get_current_user_required(
    payload: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
) -> Dict[str, Any]:
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Auth required")
    return payload


# ------------------- Helpers -------------------
def serialize_user_doc(doc: Dict[str, Any]) -> PublicUser:
    created = doc.get("created_at")
    if isinstance(created, str):
        try:
            created = datetime.fromisoformat(created)
        except ValueError:
            created = datetime.now(timezone.utc)
    return PublicUser(
        id=doc["id"],
        email=doc["email"],
        name=doc.get("name"),
        created_at=created or datetime.now(timezone.utc),
    )


def new_user_id() -> str:
    return f"user_{uuid.uuid4().hex[:12]}"
