import hashlib
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError

from app.config import settings

ALGORITHM = "HS256"


def hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode()).hexdigest()


def create_access_token(user_id: uuid.UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": str(user_id), "type": "access", "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def create_refresh_token(user_id: uuid.UUID) -> tuple[str, str, datetime]:
    """Devuelve (raw_token, token_hash, expires_at). Guardar solo el hash en BD."""
    jti = str(uuid.uuid4())
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    payload = {"sub": str(user_id), "type": "refresh", "jti": jti, "exp": expire}
    raw = jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)
    return raw, hash_token(raw), expire


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])


_PRE_AUTH_EXPIRE_MINUTES = 5
_ADMIN_TOKEN_EXPIRE_HOURS = 2


def create_pre_auth_token(admin_id: uuid.UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=_PRE_AUTH_EXPIRE_MINUTES)
    payload = {"sub": str(admin_id), "step": "mfa_pending", "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def create_admin_token(admin_id: uuid.UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=_ADMIN_TOKEN_EXPIRE_HOURS)
    payload = {"sub": str(admin_id), "role": "admin", "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_pre_auth_token(token: str) -> dict:
    from app.core.exceptions import UnauthorizedError
    data = decode_token(token)
    if data.get("step") != "mfa_pending":
        raise UnauthorizedError("Token de pre-autenticación inválido.")
    return data


def decode_admin_token(token: str) -> dict:
    from app.core.exceptions import ForbiddenError
    data = decode_token(token)
    if data.get("role") != "admin":
        raise ForbiddenError("Acceso restringido al área de administración.")
    return data
